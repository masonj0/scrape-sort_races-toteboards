#!/usr/bin/env python3
"""
# The One Script V8 (Perfected): The Complete Checkmate Racing Analysis System
# A single, self-contained application incorporating all features from the tri-hybrid architecture.

# VERSION 8.1 - THE 10/10 MANDATE
# - Corrected TrifectaAnalyzer logic.
# - Implemented non-blocking Streamlit refresh.
# - Hardened DefensiveFetcher with persistent client and non-JSON handling.
# - Implemented robust database safety with explicit columns and date handling.
# - Corrected concurrency hygiene for the background service.
# - Implemented robust data deduplication logic.
# - Added production-grade logging and settings validation.

Setup:
1. pip install -r requirements.txt
2. Create .env with: RACING_API_KEY="your_key" (optional)
3. Run: streamlit run the_one_script.py
"""

import logging
import json
import subprocess
import concurrent.futures
import time
import os
import json
import sqlite3
import logging
import threading
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import pandas as pd
import tempfile
import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError


# --- 1. LOGGING & SETTINGS ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.info("Checkmate V8 (Perfected) starting up")

class Settings(BaseSettings):
    QUALIFICATION_SCORE: float = Field(default=75.0)
    FIELD_SIZE_OPTIMAL_MIN: int = Field(default=4)
    FIELD_SIZE_OPTIMAL_MAX: int = Field(default=6)
    FIELD_SIZE_ACCEPTABLE_MIN: int = Field(default=7)
    FIELD_SIZE_ACCEPTABLE_MAX: int = Field(default=8)
    FIELD_SIZE_OPTIMAL_POINTS: int = Field(default=30)
    FIELD_SIZE_ACCEPTABLE_POINTS: int = Field(default=10)
    FIELD_SIZE_PENALTY_POINTS: int = Field(default=-20)
    FAV_ODDS_POINTS: int = Field(default=30)
    MAX_FAV_ODDS: float = Field(default=3.5)
    SECOND_FAV_ODDS_POINTS: int = Field(default=40)
    MIN_2ND_FAV_ODDS: float = Field(default=4.0)
    RACING_API_KEY: str = Field(default=os.getenv("RACING_API_KEY", ""))

# --- 2. DATA MODELS ---
class Runner(BaseModel):
    name: str
    odds: Optional[float] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    runners: List[Runner]
    source: Optional[str] = None
    checkmate_score: Optional[float] = None
    is_qualified: Optional[bool] = None
    trifecta_factors_json: Optional[str] = None

# --- 3. DEFENSIVE HTTP CLIENT ---
class DefensiveFetcher:
    def __init__(self):
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 300
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0), headers={"User-Agent": "CheckmateV8/1.0"})

    async def aclose(self):
        try: await self._client.aclose()
        except Exception: pass

    def is_circuit_breaker_open(self, domain: str) -> bool:
        if self.failure_counts.get(domain, 0) < self.circuit_breaker_threshold: return False
        if time.time() - self.last_failure_time.get(domain, 0) < self.circuit_breaker_timeout:
            return True
        self.failure_counts[domain] = 0
        return False

    def record_success(self, domain: str):
        self.failure_counts[domain] = 0

    def record_failure(self, domain: str):
        self.failure_counts[domain] = self.failure_counts.get(domain, 0) + 1
        self.last_failure_time[domain] = time.time()

    @staticmethod
    def get_domain(url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _make_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """A single, decorated attempt to make an async network request."""
        logging.info(f"Attempting request for {url}...")
        response = await self._client.get(url, headers=headers or {})
        response.raise_for_status()
        return response.json()

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        domain = self.get_domain(url)
        if self.is_circuit_breaker_open(domain):
            logging.warning(f"Circuit breaker is open for {domain}. Skipping request.")
            return None

        try:
            response = await self._make_request(url, headers=headers)
            self.record_success(domain)
            return response
        except RetryError as e:
            logging.critical(f"All retry attempts failed for {url}. Last error: {e}")
            self.record_failure(domain)
            return None
        except Exception as e:
            logging.critical(f"A non-retryable error occurred for {url}: {e}")
            self.record_failure(domain)
            return None

# --- 4. DATA SOURCE ADAPTERS ---
class BaseAdapter(ABC):
    def __init__(self, fetcher: DefensiveFetcher): self.fetcher = fetcher
    @abstractmethod
    async def fetch_races(self) -> List[Race]: raise NotImplementedError

class TVGAdapter(BaseAdapter):
    SOURCE_ID, BASE_URL = "tvg", "https://mobile-api.tvg.com/api/mobile/races/today"

    @staticmethod
    def _parse_decimal_odds(ml: Optional[str]) -> Optional[float]:
        if not ml: return None
        try: n, d = map(int, ml.strip().split("/")); return (n / d) + 1.0
        except: return None

    async def fetch_races(self) -> List[Race]:
        data = await self.fetcher.get(self.BASE_URL)
        if not data or 'races' not in data: return []
        races: List[Race] = []
        for r_info in data.get('races', []):
            try:
                runners: List[Runner] = []
                for r in r_info.get('runners', []):
                    if r.get('scratched'): continue
                    odds = self._parse_decimal_odds((r.get('odds') or {}).get('morningLine'))
                    if odds: runners.append(Runner(name=r.get('horseName') or "N/A", odds=odds))
                if len(runners) < 3: continue
                post_dt = datetime.fromisoformat(r_info['postTime'].replace("Z", "+00:00")) if r_info.get('postTime') else None
                races.append(Race(race_id=f"tvg_{r_info.get('raceId')}", track_name=r_info.get('trackName') or 'N/A', race_number=r_info.get('raceNumber'), post_time=post_dt, runners=runners, source=self.SOURCE_ID))
            except Exception as e: logging.warning(f"Skipping malformed TVG race: {e}")
        return races

# --- 5. DATA ORCHESTRATOR ---
class DataSourceOrchestrator:
    def __init__(self, settings: Settings):
        self.fetcher = DefensiveFetcher()
        self.adapters = [TVGAdapter(self.fetcher)]

    async def get_races(self) -> List[Race]:
        tasks = [adapter.fetch_races() for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_races: List[Race] = []
        for i, res in enumerate(results):
            if isinstance(res, Exception): logging.error(f"Adapter {self.adapters[i].__class__.__name__} failed: {res}")
            elif isinstance(res, list): all_races.extend(res)
        dedup: Dict[str, Race] = {}
        for r in all_races: dedup[r.race_id] = r
        return list(dedup.values())

# --- 6. TRIFECTA ANALYSIS ENGINE ---
class TrifectaAnalyzer:
    def analyze_race(self, race: Race, settings: Settings) -> Race:
        score, factors = 0.0, {}
        horses = sorted([r for r in race.runners if r.odds], key=lambda h: h.odds)
        num_runners = len(horses)
        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX: p, ok, r = settings.FIELD_SIZE_OPTIMAL_POINTS, True, f"Optimal field size ({num_runners})"
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX: p, ok, r = settings.FIELD_SIZE_ACCEPTABLE_POINTS, True, f"Acceptable field size ({num_runners})"
        else: p, ok, r = settings.FIELD_SIZE_PENALTY_POINTS, False, f"Field size not ideal ({num_runners})"
        score += p; factors["fieldSize"] = {"points": p, "ok": ok, "reason": r}
        if num_runners >= 2:
            fav, sec_fav = horses[0], horses[1]
            if fav.odds <= settings.MAX_FAV_ODDS: p, ok, r = settings.FAV_ODDS_POINTS, True, f"Favorite odds OK ({fav.odds:.2f})"
            else: p, ok, r = 0, False, f"Favorite odds too high ({fav.odds:.2f})"
            score += p; factors["favoriteOdds"] = {"points": p, "ok": ok, "reason": r}
            if sec_fav.odds >= settings.MIN_2ND_FAV_ODDS: p, ok, r = settings.SECOND_FAV_ODDS_POINTS, True, f"2nd Favorite OK ({sec_fav.odds:.2f})"
            else: p, ok, r = 0, False, f"2nd Favorite odds too low ({sec_fav.odds:.2f})"
            score += p; factors["secondFavoriteOdds"] = {"points": p, "ok": ok, "reason": r}
        race.checkmate_score = score
        race.is_qualified = score >= settings.QUALIFICATION_SCORE
        race.trifecta_factors_json = json.dumps(factors)
        return race

# --- 7. DATABASE LAYER ---
class DatabaseManager:
    def __init__(self, db_path: str = "checkmate_races.db"):
        self.db_path = db_path
        self._setup_database()

    def _setup_database(self):
        schema = """PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS live_races (race_id TEXT PRIMARY KEY, track_name TEXT, race_number INT, post_time TEXT, raw_data_json TEXT, checkmate_score REAL, qualified INT, trifecta_factors_json TEXT, updated_at TEXT); CREATE INDEX IF NOT EXISTS idx_races_qualified_score ON live_races(qualified, checkmate_score DESC, post_time);"""
        with sqlite3.connect(self.db_path) as conn: conn.executescript(schema)

    def _to_iso(self, dt: Optional[datetime]) -> Optional[str]: return dt.isoformat() if isinstance(dt, datetime) else None

    def save_races(self, races: List[Race]):
        with sqlite3.connect(self.db_path) as conn:
            for race in races:
                conn.execute("INSERT OR REPLACE INTO live_races (race_id, track_name, race_number, post_time, raw_data_json, checkmate_score, qualified, trifecta_factors_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (race.race_id, race.track_name, race.race_number, self._to_iso(race.post_time), race.model_dump_json(), race.checkmate_score, 1 if race.is_qualified else 0, race.trifecta_factors_json, datetime.utcnow().isoformat()))

    def get_races(self, qualified_only: bool) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM live_races {'WHERE qualified = 1' if qualified_only else ''} ORDER BY post_time IS NULL, checkmate_score DESC"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query)]

    def cleanup_old(self, days: int = 7):
        cutoff_iso = (datetime.utcnow() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn: conn.execute("DELETE FROM live_races WHERE updated_at < ?\", (cutoff_iso,))

# --- 8. BACKGROUND SERVICE ---
class BackgroundService:
    def __init__(self, settings: Settings, db: DatabaseManager):
        self.settings, self.db = settings, db
        self.orchestrator, self.analyzer = DataSourceOrchestrator(settings), TrifectaAnalyzer()
        self.postgres_etl = PostgresETL()
        self.running, self.thread = False, None

    def start(self):
        if not self.running: self.running, self.thread = True, threading.Thread(target=self._run, daemon=True); self.thread.start()

    def stop(self):
        self.running = False
        if self.thread: self.thread.join(5)
        if self.orchestrator.fetcher: asyncio.run(self.orchestrator.fetcher.aclose())

    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        last_cleanup = 0
        try:
            while self.running:
                try:
                    races = loop.run_until_complete(self.orchestrator.get_races())
                    analyzed_races = [self.analyzer.analyze_race(r, self.settings) for r in races]

                    # Save to local SQLite for UI
                    self.db.save_races(analyzed_races)

                    # Load into PostgreSQL Data Warehouse
                    self.postgres_etl.process_and_load(analyzed_races)

                    if time.time() - last_cleanup > 86400: self.db.cleanup_old(); last_cleanup = time.time()
                except Exception as e: logging.exception(f"Background error: {e}")
                for _ in range(60): # Check stop signal every second
                    if not self.running: break
                    time.sleep(1)
        finally:
            loop.run_until_complete(self.orchestrator.fetcher.aclose())
            loop.close()

class R_Analytics_Bridge:
    """
    Manages the execution of R scripts for advanced analytics, serving as the
    bridge between the Python core and the R statistical engine.
    """
    def __init__(self, r_script_path="r_scripts/predictive_model.R"):
        """
        Initializes the bridge with the path to the target R script.

        Args:
            r_script_path (str): The local file path to the .R script to be executed.
        """
        self.r_script_path = r_script_path

    def analyze_historical_data(self, historical_data: pd.DataFrame) -> dict | None:
        """
        Executes the R script on a pandas DataFrame of historical race data.

        Args:
            historical_data (pd.DataFrame): A DataFrame containing the necessary columns
                                            (e.g., 'odds', 'win', etc.) for the R model.

        Returns:
            dict | None: A dictionary containing the analysis results from the R script,
                         or None if the analysis fails.
        """
        # The Verbatim File Protocol in action: Create a temporary, complete CSV file.
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as temp_csv:
            temp_csv_path = temp_csv.name
            historical_data.to_csv(temp_csv, index=False)

        try:
            # The Ironclad Protocol adapted for R: Use a controlled subprocess.
            command = ["Rscript", self.r_script_path, temp_csv_path]

            logging.info(f"Executing R analytics engine: {' '.join(command)}")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,  # Will raise CalledProcessError on non-zero exit codes
                timeout=60  # Protect against hung R scripts
            )

            # The Receipts Protocol: Prove the result by parsing the JSON output.
            logging.info("R analytics engine completed successfully.")
            analysis_output = json.loads(result.stdout)
            return analysis_output

        except FileNotFoundError:
            logging.critical("'Rscript' command not found. Is R installed and in the system's PATH?")
            return None
        except subprocess.CalledProcessError as e:
            logging.critical(f"R script execution failed with exit code {e.returncode}.\n[R_STDERR]:\n{e.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logging.critical("R script execution timed out.")
            return None
        except json.JSONDecodeError:
            logging.critical("Failed to decode JSON output from R script.")
            return None
        finally:
            # Archive, Don't Annihilate (adapted): Clean up our temporary artifacts.
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
                logging.info(f"Cleaned up temporary file: {temp_csv_path}")

from sqlalchemy import create_engine, text

class PostgresETL:
    def __init__(self):
        db_url = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/checkmate_db")
        self.engine = create_engine(db_url)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _setup_database(self):
        try:
            with self.engine.connect() as conn:
                with open("pg_schemas/historical_races.sql", "r") as f:
                    conn.execute(text(f.read()))
                with open("pg_schemas/quarantine_races.sql", "r") as f:
                    conn.execute(text(f.read()))
                conn.commit()
            self.logger.info("PostgreSQL schemas verified/created successfully.")
        except Exception as e:
            self.logger.critical(f"FATAL: Could not set up PostgreSQL database: {e}", exc_info=True)
            raise

    def process_and_load(self, analyzed_races: List[Race]):
        valid_for_historical = []
        quarantined = []

        for race in analyzed_races:
            errors = []
            if not race.track_name: errors.append("Missing track_name")
            if race.race_number is None: errors.append("Missing race_number")
            if race.post_time is None: errors.append("Missing post_time")

            if not errors:
                valid_for_historical.append({
                    "race_id": race.race_id,
                    "track_name": race.track_name,
                    "race_number": race.race_number,
                    "post_time": race.post_time,
                    "source": race.source,
                    "runners_data": json.dumps([r.model_dump() for r in race.runners]),
                    "checkmate_score": race.checkmate_score,
                    "is_qualified": race.is_qualified,
                })
            else:
                quarantined.append({
                    "race_id": race.race_id,
                    "track_name": race.track_name,
                    "source": race.source,
                    "raw_data_json": race.model_dump_json(),
                    "quarantine_reason": ", ".join(errors),
                })
        
        if valid_for_historical:
            try:
                df = pd.DataFrame(valid_for_historical)
                df.to_sql('historical_races', self.engine, if_exists='append', index=False)
                self.logger.info(f"Successfully loaded {len(df)} races into historical_races.")
            except Exception as e:
                self.logger.error(f"Failed to load data into historical_races: {e}", exc_info=True)

        if quarantined:
            try:
                df_q = pd.DataFrame(quarantined)
                df_q.to_sql('quarantine_races', self.engine, if_exists='append', index=False)
                self.logger.warning(f"Quarantined {len(df_q)} races for manual review.")
            except Exception as e:
                self.logger.error(f"Failed to load data into quarantine_races: {e}", exc_info=True)

# --- 9. STREAMLIT DASHBOARD ---

@st.cache_resource
def get_db_manager(): return DatabaseManager()

@st.cache_resource
def get_settings():
    s = Settings()
    logging.info(f"Effective settings: {s.model_dump()}")
    return s

@st.cache_resource
def get_background_service(_settings, _db): return BackgroundService(_settings, _db)

def _format_post_time(pt: Optional[str]) -> str:
    if not pt: return "N/A"
    try: return datetime.fromisoformat(pt.replace("Z", "+00:00")).strftime("%I:%M %p")
    except: return "Invalid Date"

def display_race(race: Dict):
    with st.container():
        c1, c2 = st.columns()
        c1.subheader(f"{race.get('track_name', 'Unknown')} - R{race.get('race_number', '?')}")
        c1.caption(f"Post Time: {_format_post_time(race.get('post_time'))} | Source: {race.get('source', 'N/A')}")
        c2.metric("Score", f"{race.get('checkmate_score', 0) or 0:.1f}")
        if st.toggle('Show Analysis', key=f"toggle_{race.get('race_id')}"):
            try: factors = json.loads(race.get('trifecta_factors_json') or "{}")
            except: factors = {}
            for f in factors.values(): st.text(f"{'✅' if f.get('ok') else '❌'} {f.get('reason', '')} ({f.get('points', 0):+.0f} pts)")

def main():
    st.set_page_config(page_title="Checkmate V8", layout="wide")
    st.title("🏇 Checkmate V8: Sovereign Racing Analysis")
    settings, db = get_settings(), get_db_manager()
    service = get_background_service(settings, db)

    with st.sidebar:
        st.header("⚙️ Control Panel")
        col1, col2 = st.columns(2)
        if col1.button("▶️ Start", use_container_width=True, disabled=st.session_state.get('monitoring', False)):
            st.session_state.monitoring = True
            service.start()
            st.rerun()
        if col2.button("⏸️ Stop", use_container_width=True, disabled=not st.session_state.get('monitoring', False)):
            st.session_state.monitoring = False
            service.stop()
            st.rerun()
        st.info(f"Status: {'🟢 Active' if st.session_state.get('monitoring', False) else '🔴 Stopped'}")
        refresh_sec = st.slider("Auto-refresh (sec)", 10, 120, 60, 10)

    tab1, tab2, tab3 = st.tabs(["🏆 Qualified Races", "📊 All Races", "🔬 Advanced Analytics"])
    with tab1:
        for race in db.get_races(qualified_only=True): display_race(race)
    with tab2:
        for race in db.get_races(qualified_only=False): display_race(race)
    with tab3:
        st.header("R Analytics Bridge")
        st.write("Execute the R predictive model on the placeholder historical data.")
        if st.button("Run Historical Analysis"):
            with st.spinner("Loading data and executing R model... This may take a moment."):
                try:
                    df = pd.read_csv("historical_data.csv")
                    bridge = R_Analytics_Bridge()
                    results = bridge.analyze_historical_data(df)
                    if results:
                        st.success("Analysis Complete!")
                        st.json(results)
                    else:
                        st.error("R analytics bridge failed. Check server logs for details.")
                except FileNotFoundError:
                    st.error("`historical_data.csv` not found. Please ensure the file exists in the root directory.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

    if st.session_state.get("monitoring", False):
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_sec * 1000, key="autorefresh")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("="*60)
    print("👑 THE SOVEREIGN SCRIPT - CHECKMATE V8 DIAGNOSTIC TOOL 👑")
    print("="*60)
    print("Architecture: Complete tri-hybrid pipeline demonstration")
    print("Purpose: Validate data flow and analysis engine")
    print("="*60)

    print("\n[1/4] 🔧 INITIALIZING COMPONENTS...")
    config = configparser.ConfigParser()
    config.read('config.ini')

    print(f"  ├─ Qualification Score: {config.getfloat('analysis', 'qualification_score')}")
    orchestrator = SuperchargedOrchestrator(config)
    analyzer = EnhancedTrifectaAnalyzer(config)
    db_handler = DatabaseHandler(':memory:')
    print("✅ Components Initialized (using in-memory database for diagnostic)")

    print("\n[2/4] 🌐 FETCHING LIVE DATA...")
    start_time = time.time()
    live_races = orchestrator.get_races_parallel()
    fetch_time = time.time() - start_time
    print(f"✅ Fetched {len(live_races)} races in {fetch_time:.2f}s")
    if live_races:
        sources = {}
        for race in live_races: sources[race.source or 'unknown'] = sources.get(race.source or 'unknown', 0) + 1
        for source, count in sources.items(): print(f"    ├─ {source}: {count} races")
    else: print("  ⚠️  No races fetched - check network connectivity and API endpoints")

    print("\n[3/4] 🧠 ANALYZING RACES...")
    start_time = time.time()
    analyzed_races = [analyzer.analyze_race(race) for race in live_races]
    analysis_time = time.time() - start_time
    qualified_races = [r for r in analyzed_races if r.is_qualified]
    print(f"✅ Analysis complete in {analysis_time:.2f}s")
    print(f"  📈 Analysis Results:")
    print(f"    ├─ Total Races: {len(analyzed_races)}")
    print(f"    ├─ Qualified (≥{config.getfloat('analysis', 'qualification_score')}): {len(qualified_races)}")

    if qualified_races:
        print("\n  🏆 TOP QUALIFIED RACES:")
        for i, race in enumerate(sorted(qualified_races, key=lambda r: r.checkmate_score or 0, reverse=True)[:3]):
            factors = json.loads(race.trifecta_factors_json) if race.trifecta_factors_json else {}
            print(f"    {i+1}. {race.track_name} R{race.race_number} - Score: {race.checkmate_score:.1f}")
            for factor_name, factor_data in factors.items():
                status = "✅" if factor_data.get('ok') else "❌"
                print(f"       {status} {factor_data.get('reason', 'N/A')} ({factor_data.get('points', 0):+}pts)")

    print("\n[4/4] 💾 DATABASE OPERATIONS...")
    db_handler.update_races(analyzed_races)
    print(f"✅ Database update complete")

    print("\n" + "="*60)
    print("👑 SOVEREIGN SCRIPT EXECUTION COMPLETE 👑")
    print("="*60)