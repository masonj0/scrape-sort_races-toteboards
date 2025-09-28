# engine.py
# The final, supercharged version of the Python Collection Service engine.


import logging
import json
import subprocess
import concurrent.futures
import time
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from cachetools import TTLCache

# --- Finalized Settings Model ---
class Settings(BaseSettings):
    QUALIFICATION_SCORE: float = 75.0
    FIELD_SIZE_OPTIMAL_MIN: int = 4
    FIELD_SIZE_OPTIMAL_MAX: int = 6
    FIELD_SIZE_ACCEPTABLE_MIN: int = 7
    FIELD_SIZE_ACCEPTABLE_MAX: int = 8
    FIELD_SIZE_OPTIMAL_POINTS: int = 30
    FIELD_SIZE_ACCEPTABLE_POINTS: int = 10
    FIELD_SIZE_PENALTY_POINTS: int = -20
    FAV_ODDS_POINTS: int = 30
    MAX_FAV_ODDS: float = 3.5
    SECOND_FAV_ODDS_POINTS: int = 40
    MIN_2ND_FAV_ODDS: float = 4.0
    DATABASE_BATCH_SIZE: int = 100
    RUST_ENGINE_TIMEOUT: int = 10
    ODDS_API_KEY: Optional[str] = None

# --- Finalized Data Models ---

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
    analysis_details: Optional[str] = None # For advanced analysis

# --- Resilient Fetcher Stub ---
class DefensiveFetcher:
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Union[dict, str, None]:

        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1"]
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)

            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=15)
            response_text = result.stdout

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logging.warning(f"Failed to decode JSON from {url}, returning raw text.")
                return response_text # Return text as fallback
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None


# --- Enhanced Adapter Stubs ---
class BaseAdapterV7(ABC):
    def __init__(self, fetcher: DefensiveFetcher, settings: Settings):\
        self.fetcher = fetcher
        self.settings = settings
    @abstractmethod
    def fetch_races(self) -> List[Race]: raise NotImplementedError

class EnhancedTVGAdapter(BaseAdapterV7):
    def fetch_races(self) -> List[Race]:
        # TODO: Implement full logic with caching as per blueprint
        return []

class TheOddsApiAdapter(BaseAdapterV7):
    def fetch_races(self) -> List[Race]:
        # TODO: Implement full logic with multi-bookmaker parsing
        return []

PRODUCTION_ADAPTERS = [EnhancedTVGAdapter, TheOddsApiAdapter] # Add others as they are built

# --- Supercharged Orchestrator ---
class SuperchargedOrchestrator:
    def __init__(self, settings: Settings):
        self.fetcher = DefensiveFetcher()
        self.settings = settings
        self.adapters = [Adapter(self.fetcher, self.settings) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_races_parallel(self) -> tuple[list[Race], list[dict]]:
        # This method will be enhanced with performance monitoring and data validation
        # For now, it implements the core concurrent fetching logic
        all_races, statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                adapter = future_to_adapter[future]
                try:
                    races = future.result()
                    all_races.extend(races)
                    # Create a basic status receipt for now
                    statuses.append({'adapter_id': adapter.__class__.__name__, 'status': 'OK', 'races_found': len(races)})
                except Exception as e:
                    self.logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}", exc_info=True)
                    statuses.append({'adapter_id': adapter.__class__.__name__, 'status': 'ERROR', 'error_message': str(e)})
        return all_races, statuses

# --- Enhanced Trifecta Analyzer Stub ---
class EnhancedTrifectaAnalyzer:
    def __init__(self, settings: Settings):
        self.settings = settings
        # TODO: Load ML model and historical data

    def analyze_race_advanced(self, race: Race) -> Race:
        # TODO: Implement full analysis with base scoring, ML, and historical factors
        race.checkmate_score = 50.0 # Placeholder
        race.is_qualified = race.checkmate_score >= self.settings.QUALIFICATION_SCORE
        race.analysis_details = json.dumps({'base_score': 50.0})

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
    def __init__(self, fetcher: DefensiveFetcher): self.fetcher = fetcher
    @abstractmethod
    def fetch_races(self) -> List[Race]: raise NotImplementedError

class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not isinstance(response_data, dict) or 'races' not in response_data:
            logging.warning(f"TVGAdapter received invalid or non-dict data: {type(response_data)}")
            return []
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
            if not isinstance(data, dict):
                logging.warning(f"BetfairExchangeAdapter received invalid or non-dict data: {type(data)}")
                return []
            parsed_races = self._parse_betfair_races(data)
            if parsed_races: races.extend(parsed_races)
        except Exception as e: logging.warning(f"Betfair endpoint failed: {e}")
        for race in races: race.source = self.SOURCE_ID
        return races

    def _parse_betfair_races(self, data: dict) -> List[Race]:
        races = []
        try:
            event_nodes = data.get('eventTypes', [{}])[0].get('eventNodes', [])
            for NotImplementedError _nodes:
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
                        if market.get('marketStartTime'):
                            try: start_time = datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00'))
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
        if not isinstance(response_data, dict) or not response_data.get('events'):
            logging.warning(f"PointsBetAdapter received invalid or non-dict data: {type(response_data)}")
            return []
        races = []
        for event in response_data['events']:
            try:
                if not event.get('winPlaceOddsAvailable'): continue
                runners = [Runner(name=o.get('name', 'Unknown'), odds=_convert_odds_to_float(o.get('price'))) for o in event.get('fixedPrice', {}).get('outcomes', []) if o.get('outcomeType') == 'Win']
                if len(runners) < 3: continue
                start_time = datetime.fromisoformat(event['startsAt'].replace('Z', '+00:00')) if event.get('startsAt') else None
                race = Race(race_id=f"pointsbet_{event.get('key', 'unknown')}", track_name=event.get('competitionName', 'Unknown Track'), race_number=event.get('eventNumber'), post_time=start_time, runners=runners, source=self.SOURCE_ID)
                races.append(race)
            except Exception as e:
                logging.warning(f"Skipping malformed PointsBet event: {e}")
                continue
        return races

PRODUCTION_ADAPTERS = [TVGAdapter, BetfairExchangeAdapter, PointsBetAdapter]

# --- Orchestrator ---
class DataSourceOrchestrator:
    def __init__(self):
        self.fetcher = DefensiveFetcher()
        self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch_from_adapter(self, adapter: BaseAdapterV7) -> tuple[list[Race], dict]:
        adapter_id = adapter.__class__.__name__
        start_time = time.time()
        status = {"adapter_id": adapter_id, "timestamp": datetime.now(), "status": "ERROR", "races_found": 0, "error_message": "Unknown error", "response_time": 0}
        try:
            races = adapter.fetch_races()
            end_time = time.time()
            status.update({"status": "OK", "races_found": len(races), "error_message": None, "response_time": end_time - start_time})
            return races, status
        except Exception as e:
            end_time = time.time()
            self.logger.error(f"Adapter {adapter_id} failed: {e}", exc_info=True)
            status.update({"error_message": str(e), "response_time": end_time - start_time})
            return [], status

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                try:
                    races, status = future.result()
                    if races: all_races.extend(races)
                    statuses.append(status)
                except Exception as e:
                    adapter_id = future_to_adapter[future].__class__.__name__
                    self.logger.critical(f"A future for {adapter_id} failed unexpectedly: {e}", exc_info=True)
                    statuses.append({"adapter_id": adapter_id, "timestamp": datetime.now(), "status": "ERROR", "races_found": 0, "error_message": f"Future failed: {e}", "response_time": 0})
        self.logger.info(f"Orchestrator fetched a total of {len(all_races)} races from {len(self.adapters)} adapters.")
        return all_races, statuses

# --- Analyzer ---
class TrifectaAnalyzer:
    def analyze_race(self, race: Race, settings: Settings) -> Race:
        score = 0
        trifecta_factors = {}
        horses_with_odds = sorted([r for r in race.runners if r.odds], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)

        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX:
            points, ok, reason = settings.FIELD_SIZE_OPTIMAL_POINTS, True, f"Optimal field size ({num_runners})"
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX:
            points, ok, reason = settings.FIELD_SIZE_ACCEPTABLE_POINTS, True, f"Acceptable field size ({num_runners})"
        else:
            points, ok, reason = settings.FIELD_SIZE_PENALTY_POINTS, False, f"Field size not ideal ({num_runners})"
        score += points
        trifecta_factors["fieldSize"] = {"points": points, "ok": ok, "reason": reason}

        if num_runners >= 2:
            fav, sec_fav = horses_with_odds[0], horses_with_odds[1]
            if fav.odds <= settings.MAX_FAV_ODDS:
                points, ok, reason = settings.FAV_ODDS_POINTS, True, f"Favorite odds OK ({fav.odds:.2f})"
            else:
                points, ok, reason = 0, False, f"Favorite odds too high ({fav.odds:.2f})"
            score += points
            trifecta_factors["favoriteOdds"] = {"points": points, "ok": ok, "reason": reason}

            if sec_fav.odds >= settings.MIN_2ND_FAV_ODDS:
                points, ok, reason = settings.SECOND_FAV_ODDS_POINTS, True, f"2nd Favorite OK ({sec_fav.odds:.2f})"
            else:
                points, ok, reason = 0, False, f"2nd Favorite odds too low ({sec_fav.odds:.2f})"
            score += points
            trifecta_factors["secondFavoriteOdds"] = {"points": points, "ok": ok, "reason": reason}

        race.checkmate_score = score
        race.is_qualified = score >= settings.QUALIFICATION_SCORE
        race.trifecta_factors_json = json.dumps(trifecta_factors)

        return race