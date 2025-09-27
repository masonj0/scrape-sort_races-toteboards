# engine.py
# Fully activated with the complete data fleet and analysis engine.

import logging
import json
import subprocess
import sqlite3
import concurrent.futures
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# --- Professional Settings Management ---
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

# --- Data Models ---
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

# --- Hardened Database Handler ---
class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _get_connection(self):
        # timeout parameter helps with SQLITE_BUSY errors
        return sqlite3.connect(self.db_path, timeout=10)

    def _setup_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 'live_races' table now includes pre-calculated results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_races (
                    race_id TEXT PRIMARY KEY,
                    track_name TEXT,
                    post_time DATETIME,
                    source TEXT,
                    checkmate_score REAL,
                    is_qualified INTEGER,
                    data_json TEXT,
                    updated_at DATETIME
                );
            """)
            # 'events' table for the 'Reliable Trigger' protocol
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            self.logger.info(f"Hardened database initialized successfully at {self.db_path}")

    def update_races(self, races: List[Race]):
        # This method will be expanded with retry logic
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for race in races:
                cursor.execute("""
                    INSERT OR REPLACE INTO live_races
                    (race_id, track_name, post_time, source, checkmate_score, is_qualified, data_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    race.race_id, race.track_name, race.post_time, race.source,
                    race.checkmate_score, race.is_qualified,
                    race.model_dump_json(), datetime.now()
                ))
            # Fire the reliable trigger for the C# app
            if races:
                cursor.execute("""
                    INSERT INTO events (event_type, payload) VALUES (?, ?)
                """, ("RACES_UPDATED", json.dumps({"race_count": len(races)})))
            conn.commit()

# --- Battle-Tested Fetcher ---
class DefensiveFetcher:
    def get(self, url: str, response_type: str = 'auto', headers: Optional[Dict[str, str]] = None) -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1"]
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=15)
            response_text = result.stdout
            if response_type == 'text': return response_text
            try: return json.loads(response_text)
            except json.JSONDecodeError: return response_text
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

# --- Adapters ---
def _convert_odds_to_float(odds_str: Optional[Union[str, float]]) -> Optional[float]:
    if isinstance(odds_str, float): return odds_str
    if not odds_str or not isinstance(odds_str, str): return None
    odds_str = odds_str.strip().upper()
    if odds_str in ['SP', 'SCRATCHED']: return None
    if odds_str in ['EVS', 'EVENS']: return 2.0
    if '/' in odds_str:
        try:
            num, den = map(int, odds_str.split('/'))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, ZeroDivisionError): return None
    try: return float(odds_str)
    except (ValueError, TypeError): return None

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher
    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError

class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or 'races' not in response_data: return []
        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = [Runner(name=r.get('horseName', 'N/A'), odds=self._parse_odds(r.get('odds'))) for r in race_info.get('runners', []) if not r.get('scratched') and self._parse_odds(r.get('odds')) is not None]
                if not runners: continue
                all_races.append(Race(race_id=f"tvg_{race_info.get('raceId')}", track_name=race_info.get('trackName', 'N/A'), race_number=race_info.get('raceNumber'), post_time=datetime.fromisoformat(race_info.get('postTime').replace('Z', '+00:00')) if race_info.get('postTime') else None, runners=runners, source=self.SOURCE_ID))
            except Exception: continue
        return all_races

    def _parse_odds(self, odds_data: Optional[Dict]) -> Optional[float]:
        if not odds_data or odds_data.get('morningLine') is None: return None
        try:
            num, den = map(int, odds_data['morningLine'].split('/'))
            return (num / den) + 1.0
        except (ValueError, TypeError, ZeroDivisionError): return None

class BetfairExchangeAdapter(BaseAdapterV7):
    SOURCE_ID = "betfair_exchange"

    def fetch_races(self) -> List[Race]:
        races = []
        endpoint = "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?alt=json&filter=canonical&maxResults=25&rollupLimit=2&types=EVENT,MARKET_DESCRIPTION,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST,MARKET_STATE&marketProjection=EVENT,MARKET_START_TIME,RUNNER_DESCRIPTION&eventTypeIds=7"
        try:
            data = self.fetcher.get(endpoint, response_type='json', headers={'Accept': 'application/json'})
            if data:
                parsed_races = self._parse_betfair_races(data)
                if parsed_races:
                    races.extend(parsed_races)
        except Exception as e:
            logging.warning(f"Betfair endpoint failed: {e}")
        for race in races: race.source = self.SOURCE_ID
        return races

    def _parse_betfair_races(self, data: dict) -> List[Race]:
        races = []
        try:
            event_nodes = data.get('eventTypes', [{}])[0].get('eventNodes', [])
            for event_node in event_nodes:
                event = event_node.get('event', {})
                for market_node in event_node.get('marketNodes', []):
                    market = market_node.get('market', {})
                    if market.get('marketType', '') != 'WIN': continue
                    runners = []
                    for runner in market_node.get('runners', []):
                        if runner.get('state', {}).get('status') != 'ACTIVE': continue
                        odds = None
                        if 'exchange' in runner:
                            available_to_back = runner['exchange'].get('availableToBack', [])
                            if available_to_back: odds = available_to_back[0].get('price')
                        runners.append(Runner(name=runner.get('description', {}).get('runnerName', 'Unknown'), odds=odds))
                    if len(runners) >= 3:
                        start_time = None
                        time_field = market.get('marketStartTime')
                        if time_field:
                            try: start_time = datetime.fromisoformat(time_field.replace('Z', '+00:00'))
                            except: pass
                        race = Race(race_id=f"betfair_{market.get('marketId', 'unknown')}", track_name=event.get('venue', 'Betfair Exchange'), post_time=start_time, race_number=int(event.get('eventName', '0').split('R')[-1]) if 'R' in event.get('eventName', '') else None, runners=runners)
                        races.append(race)
        except Exception as e: logging.error(f"Error parsing Betfair data structure: {e}")
        return races

class PointsBetAdapter(BaseAdapterV7):
    SOURCE_ID = "pointsbet"
    BASE_URL = "https://api.nj.pointsbet.com/api/v2/sports/horse-racing/events/upcoming?page=1"

    def fetch_races(self) -> List[Race]:
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or not response_data.get('events'):
            return []

        races = []
        for event in response_data['events']:
            try:
                if not event.get('winPlaceOddsAvailable'):
                    continue

                runners = []
                for outcome in event.get('fixedPrice', {}).get('outcomes', []):
                    if outcome.get('outcomeType') != 'Win':
                        continue
                    runners.append(Runner(
                        name=outcome.get('name', 'Unknown'),
                        odds=_convert_odds_to_float(outcome.get('price'))
                    ))

                if len(runners) < 3:
                    continue

                start_time = datetime.fromisoformat(event['startsAt'].replace('Z', '+00:00')) if event.get('startsAt') else None

                race = Race(
                    race_id=f"pointsbet_{event.get('key', 'unknown')}",
                    track_name=event.get('competitionName', 'Unknown Track'),
                    race_number=event.get('eventNumber'),
                    post_time=start_time,
                    runners=runners,
                    source=self.SOURCE_ID
                )
                races.append(race)
            except Exception as e:
                logging.warning(f"Skipping malformed PointsBet event: {e}")
                continue
        return races

PRODUCTION_ADAPTERS = [TVGAdapter, BetfairExchangeAdapter, PointsBetAdapter]

# --- Concurrent Orchestrator ---
class DataSourceOrchestrator:
    def __init__(self):
        self.fetcher = DefensiveFetcher()
        self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch_from_adapter(self, adapter: BaseAdapterV7):
        try:
            return adapter.fetch_races()
        except Exception as e:
            self.logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}", exc_info=True)
            return [] # Return empty list on failure

    def get_races(self) -> List[Race]:
        all_races = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                try:
                    races = future.result()
                    if races:
                        all_races.extend(races)
                except Exception as e:
                    self.logger.critical(f"A future in the orchestrator failed unexpectedly: {e}", exc_info=True)
        self.logger.info(f"Orchestrator fetched a total of {len(all_races)} races from {len(self.adapters)} adapters.")
        return all_races

# --- Trifecta Analyzer (Full Logic) ---
class TrifectaAnalyzer:
    def analyze_race(self, race: Race, settings: Settings) -> Race:
        horses_with_odds = sorted([r for r in race.runners if r.odds], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)
        score = 0

        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX:
            score += settings.FIELD_SIZE_OPTIMAL_POINTS
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX:
            score += settings.FIELD_SIZE_ACCEPTABLE_POINTS
        else:
            score += settings.FIELD_SIZE_PENALTY_POINTS

        if num_runners >= 2:
            fav_odds = horses_with_odds[0].odds
            sec_fav_odds = horses_with_odds[1].odds
            if fav_odds <= settings.MAX_FAV_ODDS:
                score += settings.FAV_ODDS_POINTS
            if sec_fav_odds >= settings.MIN_2ND_FAV_ODDS:
                score += settings.SECOND_FAV_ODDS_POINTS

        race.checkmate_score = score
        race.is_qualified = score >= settings.QUALIFICATION_SCORE
        return race