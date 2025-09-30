# engine.py
# PRODUCTION-GRADE Python engine with all bug fixes applied

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

# --- Settings ---
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

# --- Models ---
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

# --- Universal Odds Parser (FIXED) ---
def parse_odds_universal(odds_input: any) -> Optional[float]:
    """
    Universal odds parser supporting:
    - American odds: +150, -200
    - Fractional odds: 5/2, 3/1
    - Decimal odds: 2.5, 3.75
    """
    if not odds_input:
        return None

    odds_str = str(odds_input).strip().upper()

    if odds_str in ['SP', 'SCRATCHED', 'N/A', '']:
        return None
    if odds_str in ['EVS', 'EVENS']:
        return 2.0

    if odds_str.startswith(('+', '-')):
        try:
            american = int(odds_str)
            if american > 0:
                return (american / 100) + 1
            else:
                return (100 / abs(american)) + 1
        except (ValueError, TypeError):
            return None

    if '/' in odds_str:
        try:
            num, den = map(float, odds_str.split('/'))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, ZeroDivisionError, TypeError):
            return None

    try:
        return float(odds_str)
    except (ValueError, TypeError):
        return None

# --- Safe DateTime Parser (FIXED) ---
def safe_parse_datetime(dt_input: any) -> Optional[datetime]:
    """Safely parse datetime from various formats."""
    if not dt_input:
        return None

    dt_str = str(dt_input).strip()

    try:
        if 'Z' in dt_str:
            dt_str = dt_str.replace('Z', '+00:00')
        return datetime.fromisoformat(dt_str)
    except (ValueError, AttributeError):
        return None

# --- Defensive Fetcher ---
class DefensiveFetcher:
    """HTTP client using subprocess curl for maximum reliability."""

    def get(self, url: str, response_type: str = 'auto',
            headers: Optional[Dict[str, str]] = None) -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1", "--max-time", "15"]

            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])

            command.append(url)

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=20
            )
            response_text = result.stdout

            if response_type == 'text':
                return response_text

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logging.warning(f"Response from {url} is not JSON, returning text")
                return response_text

        except subprocess.TimeoutExpired:
            logging.error(f"Request to {url} timed out")
            return None
        except subprocess.CalledProcessError as e:
            logging.error(f"curl failed for {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
            return None

# --- Base Adapter ---
class BaseAdapterV7(ABC):
    """Base class for all data source adapters."""

    def __init__(self, fetcher: DefensiveFetcher):
        self.fetcher = fetcher
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError

# --- TVG Adapter ---
class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def fetch_races(self) -> List[Race]:
        self.logger.info(f"Fetching from {self.BASE_URL}")
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')

        if not response_data or not isinstance(response_data, dict):
            self.logger.warning("Invalid response from TVG")
            return []

        if 'races' not in response_data:
            self.logger.warning("No 'races' key in TVG response")
            return []

        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = []
                for r in race_info.get('runners', []):
                    if r.get('scratched'):
                        continue

                    odds_data = r.get('odds', {})
                    odds = self._parse_tvg_odds(odds_data.get('morningLine'))

                    if odds is not None:
                        runners.append(Runner(
                            name=r.get('horseName', 'Unknown'),
                            odds=odds
                        ))

                if len(runners) < 3:
                    continue

                post_time = safe_parse_datetime(race_info.get('postTime'))

                all_races.append(Race(
                    race_id=f"tvg_{race_info.get('raceId', 'unknown')}",
                    track_name=race_info.get('trackName', 'TVG Track'),
                    race_number=race_info.get('raceNumber'),
                    post_time=post_time,
                    runners=runners,
                    source=self.SOURCE_ID
                ))

            except Exception as e:
                self.logger.warning(f"Failed to parse TVG race: {e}")
                continue

        self.logger.info(f"Successfully fetched {len(all_races)} races from TVG")
        return all_races

    def _parse_tvg_odds(self, odds_data: any) -> Optional[float]:
        if not odds_data:
            return None
        try:
            if isinstance(odds_data, str) and '/' in odds_data:
                num, den = map(int, odds_data.split('/'))
                return (num / den) + 1.0 if den != 0 else None
            return parse_odds_universal(odds_data)
        except (ValueError, TypeError, ZeroDivisionError):
            return None

# --- Betfair Adapter ---
class BetfairExchangeAdapter(BaseAdapterV7):
    SOURCE_ID = "betfair_exchange"
    BASE_URL = "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket"

    def fetch_races(self) -> List[Race]:
        self.logger.info("Fetching from Betfair Exchange")

        params = {
            'alt': 'json',
            'filter': 'canonical',
            'maxResults': '25',
            'rollupLimit': '2',
            'types': 'EVENT,MARKET_DESCRIPTION,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST,MARKET_STATE',
            'marketProjection': 'EVENT,MARKET_START_TIME,RUNNER_DESCRIPTION',
            'eventTypeIds': '7'
        }

        url = f"{self.BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        data = self.fetcher.get(url, response_type='json', headers={'Accept': 'application/json'})

        if not data or not isinstance(data, dict):
            self.logger.warning("Invalid response from Betfair")
            return []

        races = self._parse_betfair_data(data)
        self.logger.info(f"Successfully fetched {len(races)} races from Betfair")
        return races

    def _parse_betfair_data(self, data: dict) -> List[Race]:
        races = []

        try:
            event_types = data.get('eventTypes', [])
            if not event_types:
                return races

            event_nodes = event_types[0].get('eventNodes', [])

            for event_node in event_nodes:
                event = event_node.get('event', {})

                for market_node in event_node.get('marketNodes', []):
                    market = market_node.get('market', {})

                    if market.get('marketType', '') != 'WIN':
                        continue

                    runners = []
                    for runner in market_node.get('runners', []):
                        if runner.get('state', {}).get('status') != 'ACTIVE':
                            continue

                        odds = None
                        exchange_data = runner.get('exchange', {})
                        available_to_back = exchange_data.get('availableToBack', [])

                        if available_to_back and len(available_to_back) > 0:
                            odds = available_to_back[0].get('price')

                        runners.append(Runner(
                            name=runner.get('description', {}).get('runnerName', 'Unknown'),
                            odds=odds
                        ))

                    if len(runners) < 3:
                        continue

                    post_time = safe_parse_datetime(market.get('marketStartTime'))

                    race_number = None
                    event_name = event.get('eventName', '')
                    if 'R' in event_name:
                        try:
                            race_number = int(event_name.split('R')[-1])
                        except (ValueError, IndexError):
                            pass

                    race = Race(
                        race_id=f"betfair_{market.get('marketId', 'unknown')}",
                        track_name=event.get('venue', 'Betfair Exchange'),
                        post_time=post_time,
                        race_number=race_number,
                        runners=runners,
                        source=self.SOURCE_ID
                    )
                    races.append(race)

        except Exception as e:
            self.logger.error(f"Error parsing Betfair data: {e}", exc_info=True)

        return races

# --- PointsBet Adapter ---
class PointsBetAdapter(BaseAdapterV7):
    SOURCE_ID = "pointsbet"
    BASE_URL = "https://api.nj.pointsbet.com/api/v2/sports/horse-racing/events/upcoming?page=1"

    def fetch_races(self) -> List[Race]:
        self.logger.info("Fetching from PointsBet")
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')

        if not response_data or not isinstance(response_data, dict):
            self.logger.warning("Invalid response from PointsBet")
            return []

        events = response_data.get('events', [])
        if not events:
            self.logger.warning("No events in PointsBet response")
            return []

        races = []
        for event in events:
            try:
                if not event.get('winPlaceOddsAvailable'):
                    continue

                runners = []
                fixed_price = event.get('fixedPrice', {})
                outcomes = fixed_price.get('outcomes', [])

                for outcome in outcomes:
                    if outcome.get('outcomeType') == 'Win':
                        odds = parse_odds_universal(outcome.get('price'))
                        runners.append(Runner(
                            name=outcome.get('name', 'Unknown'),
                            odds=odds
                        ))

                if len(runners) < 3:
                    continue

                post_time = safe_parse_datetime(event.get('startsAt'))

                race = Race(
                    race_id=f"pointsbet_{event.get('key', 'unknown')}",
                    track_name=event.get('competitionName', 'Unknown Track'),
                    race_number=event.get('eventNumber'),
                    post_time=post_time,
                    runners=runners,
                    source=self.SOURCE_ID
                )
                races.append(race)

            except Exception as e:
                self.logger.warning(f"Failed to parse PointsBet event: {e}")
                continue

        self.logger.info(f"Successfully fetched {len(races)} races from PointsBet")
        return races

# --- Data Source Orchestrator ---
class DataSourceOrchestrator:
    """Coordinates concurrent fetching from multiple adapters."""

    def __init__(self):
        self.fetcher = DefensiveFetcher()
        self.adapters: List[BaseAdapterV7] = [
            TVGAdapter(self.fetcher),
            BetfairExchangeAdapter(self.fetcher),
            PointsBetAdapter(self.fetcher)
        ]
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch_from_adapter(self, adapter: BaseAdapterV7) -> tuple[list[Race], dict]:
        adapter_id = adapter.__class__.__name__
        start_time = time.time()

        status = {
            "adapter_id": adapter_id,
            "timestamp": datetime.now(),
            "status": "FAILURE",
            "races_found": 0,
            "response_time": 0.0,
            "error_message": None
        }

        try:
            races = adapter.fetch_races()
            status["status"] = "SUCCESS"
            status["races_found"] = len(races)
            return races, status
        except Exception as e:
            self.logger.error(f"Adapter {adapter_id} failed: {e}", exc_info=True)
            status["error_message"] = str(e)
            return [], status
        finally:
            status["response_time"] = time.time() - start_time

    def get_races(self) -> tuple[list[Race], list[dict]]:
        self.logger.info(f"Starting concurrent fetch from {len(self.adapters)} adapters...")
        all_races = []
        all_statuses = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}

            for future in concurrent.futures.as_completed(future_to_adapter):
                try:
                    races, status = future.result()
                    all_races.extend(races)
                    all_statuses.append(status)
                except Exception as e:
                    adapter_name = future_to_adapter[future].__class__.__name__
                    self.logger.critical(f"Future for adapter {adapter_name} generated an unexpected error: {e}")
                    all_statuses.append({
                        "adapter_id": adapter_name,
                        "timestamp": datetime.now(),
                        "status": "CRITICAL_FAILURE",
                        "races_found": 0,
                        "response_time": 0.0,
                        "error_message": f"Unhandled exception: {e}"
                    })

        self.logger.info(f"Concurrent fetch complete. Total races: {len(all_races)}")
        return all_races, all_statuses

# --- Trifecta Analyzer ---
class TrifectaAnalyzer:
    """Analyzes and scores races based on Checkmate criteria."""

    def analyze_race(self, race: Race, settings: Settings) -> Race:
        score = 0.0
        factors = {}

        runners_with_odds = sorted([r for r in race.runners if r.odds], key=lambda r: r.odds)
        num_runners = len(runners_with_odds)

        # Field Size
        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX:
            score += settings.FIELD_SIZE_OPTIMAL_POINTS
            factors['fieldSize'] = {'points': settings.FIELD_SIZE_OPTIMAL_POINTS, 'ok': True, 'reason': f"Optimal size ({num_runners})"}
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX:
            score += settings.FIELD_SIZE_ACCEPTABLE_POINTS
            factors['fieldSize'] = {'points': settings.FIELD_SIZE_ACCEPTABLE_POINTS, 'ok': True, 'reason': f"Acceptable size ({num_runners})"}
        else:
            score += settings.FIELD_SIZE_PENALTY_POINTS
            factors['fieldSize'] = {'points': settings.FIELD_SIZE_PENALTY_POINTS, 'ok': False, 'reason': f"Not ideal size ({num_runners})"}

        # Odds Analysis
        if num_runners >= 2:
            fav_odds = runners_with_odds[0].odds
            sec_fav_odds = runners_with_odds[1].odds

            if fav_odds <= settings.MAX_FAV_ODDS:
                score += settings.FAV_ODDS_POINTS
                factors['favoriteOdds'] = {'points': settings.FAV_ODDS_POINTS, 'ok': True, 'reason': f"Fav odds OK ({fav_odds:.2f})"}
            else:
                factors['favoriteOdds'] = {'points': 0, 'ok': False, 'reason': f"Fav odds too high ({fav_odds:.2f})"}

            if sec_fav_odds >= settings.MIN_2ND_FAV_ODDS:
                score += settings.SECOND_FAV_ODDS_POINTS
                factors['secondFavoriteOdds'] = {'points': settings.SECOND_FAV_ODDS_POINTS, 'ok': True, 'reason': f"2nd Fav OK ({sec_fav_odds:.2f})"}
            else:
                factors['secondFavoriteOdds'] = {'points': 0, 'ok': False, 'reason': f"2nd Fav odds too low ({sec_fav_odds:.2f})"}

        race.checkmate_score = score
        race.is_qualified = score >= settings.QUALIFICATION_SCORE
        race.trifecta_factors_json = json.dumps(factors)

        return race