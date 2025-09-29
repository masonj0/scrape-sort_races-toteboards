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

import asyncio
import streamlit as st
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

    def record_success(self, domain: str): self.failure_counts[domain] = 0
    def record_failure(self, domain: str):
        self.failure_counts[domain] = self.failure_counts.get(domain, 0) + 1
        self.last_failure_time[domain] = time.time()

    @staticmethod
    def get_domain(url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        domain = self.get_domain(url)
        if self.is_circuit_breaker_open(domain):
            logging.warning(f"Circuit breaker open for {domain}")
            return None
        for attempt in range(3):
            try:
                response = await self._client.get(url, headers=headers or {})
                response.raise_for_status()
                self.record_success(domain)
                return response.json()
            except (httpx.HTTPError, json.JSONDecodeError) as e:
                wait = (2 ** attempt) + (0.1 * attempt)
                logging.warning(f"HTTP/JSON failure from {domain} (attempt {attempt+1}): {e}. Backing off {wait:.1f}s")
                if attempt == 2: self.record_failure(domain)
                await asyncio.sleep(wait)
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
                    analyzed = [self.analyzer.analyze_race(r, self.settings) for r in races]
                    self.db.save_races(analyzed)
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
    main()