#!/usr/bin/env python3
# ==============================================================================
# == Checkmate V8 - The Ultimate Engine (FINAL CORRECTED VERBATIM)
# ==============================================================================

import logging
import json
import subprocess
import concurrent.futures
import time
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from bs4 import BeautifulSoup

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

# --- Universal Helpers ---
def parse_odds_universal(odds_input: any) -> Optional[float]:
    if not odds_input: return None
    odds_str = str(odds_input).strip().upper()
    if odds_str in ['SP', 'SCRATCHED', 'N/A', '']: return None
    if odds_str in ['EVS', 'EVENS']: return 2.0
    if odds_str.startswith(('+', '-')):
        try:
            american = int(odds_str)
            if american > 0: return (american / 100) + 1
            else: return (100 / abs(american)) + 1
        except (ValueError, TypeError): return None
    if '/' in odds_str:
        try:
            num, den = map(float, odds_str.split('/'))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, ZeroDivisionError, TypeError): return None
    try: return float(odds_str)
    except (ValueError, TypeError): return None

def safe_parse_datetime(dt_input: any) -> Optional[datetime]:
    if not dt_input: return None
    dt_str = str(dt_input).strip()
    try:
        if 'Z' in dt_str: dt_str = dt_str.replace('Z', '+00:00')
        return datetime.fromisoformat(dt_str)
    except (ValueError, AttributeError): return None

# --- CORE Components ---
class DefensiveFetcher:
    def get(self, url: str, response_type: str = 'auto', headers: Optional[Dict[str, str]] = None) -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1", "--max-time", "15"]
            if headers: [command.extend(["-H", f"{k}: {v}"]) for k, v in headers.items()]
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=20)
            if response_type == 'text': return result.stdout
            try: return json.loads(result.stdout)
            except json.JSONDecodeError: return result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            logging.error(f"Error fetching {url}: {e}"); return None

class BaseAdapterV7(ABC):
    def __init__(self, fetcher: DefensiveFetcher): self.fetcher = fetcher; self.logger = logging.getLogger(self.__class__.__name__)
    @abstractmethod
    def fetch_races(self) -> List[Race]: raise NotImplementedError

class TrifectaAnalyzer:
    def analyze_race(self, race: Race, settings: Settings) -> Race:
        score, factors = 0.0, {}
        runners_with_odds = sorted([r for r in race.runners if r.odds], key=lambda r: r.odds)
        num_runners = len(runners_with_odds)
        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX: score += settings.FIELD_SIZE_OPTIMAL_POINTS; factors['fieldSize'] = {'points': settings.FIELD_SIZE_OPTIMAL_POINTS, 'ok': True, 'reason': f"Optimal size ({num_runners})"}
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX: score += settings.FIELD_SIZE_ACCEPTABLE_POINTS; factors['fieldSize'] = {'points': settings.FIELD_SIZE_ACCEPTABLE_POINTS, 'ok': True, 'reason': f"Acceptable size ({num_runners})"}
        else: score += settings.FIELD_SIZE_PENALTY_POINTS; factors['fieldSize'] = {'points': settings.FIELD_SIZE_PENALTY_POINTS, 'ok': False, 'reason': f"Not ideal size ({num_runners})"}
        if num_runners >= 2:
            fav_odds, sec_fav_odds = runners_with_odds[0].odds, runners_with_odds[1].odds
            if fav_odds <= settings.MAX_FAV_ODDS: score += settings.FAV_ODDS_POINTS; factors['favoriteOdds'] = {'points': settings.FAV_ODDS_POINTS, 'ok': True, 'reason': f"Fav odds OK ({fav_odds:.2f})"}
            else: factors['favoriteOdds'] = {'points': 0, 'ok': False, 'reason': f"Fav odds too high ({fav_odds:.2f})"}
            if sec_fav_odds >= settings.MIN_2ND_FAV_ODDS: score += settings.SECOND_FAV_ODDS_POINTS; factors['secondFavoriteOdds'] = {'points': settings.SECOND_FAV_ODDS_POINTS, 'ok': True, 'reason': f"2nd Fav OK ({sec_fav_odds:.2f})"}
            else: factors['secondFavoriteOdds'] = {'points': 0, 'ok': False, 'reason': f"2nd Fav odds too low ({sec_fav_odds:.2f})"}
        race.checkmate_score = score; race.is_qualified = score >= settings.QUALIFICATION_SCORE; race.trifecta_factors_json = json.dumps(factors)
        return race

# --- CORE Adapters (COMPLETE AND VERBATIM) ---
class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        self.logger.info(f"Fetching from {self.BASE_URL}")
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or not isinstance(response_data, dict) or 'races' not in response_data: self.logger.warning("Invalid or empty response from TVG"); return []
        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = [Runner(name=r.get('horseName', 'Unknown'), odds=self._parse_tvg_odds(r.get('odds', {}).get('morningLine'))) for r in race_info.get('runners', []) if not r.get('scratched') and self._parse_tvg_odds(r.get('odds', {}).get('morningLine')) is not None]
                if len(runners) < 3: continue
                all_races.append(Race(race_id=f"tvg_{race_info.get('raceId', 'unknown')}", track_name=race_info.get('trackName', 'TVG Track'), race_number=race_info.get('raceNumber'), post_time=safe_parse_datetime(race_info.get('postTime')), runners=runners, source=self.SOURCE_ID))
            except Exception as e: self.logger.warning(f"Failed to parse TVG race: {e}")
        self.logger.info(f"Successfully fetched {len(all_races)} races from TVG"); return all_races
    def _parse_tvg_odds(self, odds_data: any) -> Optional[float]:
        if not odds_data: return None
        try:
            if isinstance(odds_data, str) and '/' in odds_data: num, den = map(int, odds_data.split('/')); return (num / den) + 1.0 if den != 0 else None
            return parse_odds_universal(odds_data)
        except (ValueError, TypeError, ZeroDivisionError): return None

class BetfairExchangeAdapter(BaseAdapterV7):
    SOURCE_ID = "betfair_exchange"; BASE_URL = "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket"
    def fetch_races(self) -> List[Race]:
        self.logger.info("Fetching from Betfair Exchange")
        params = {'alt': 'json', 'filter': 'canonical', 'maxResults': '25', 'rollupLimit': '2', 'types': 'EVENT,MARKET_DESCRIPTION,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST,MARKET_STATE', 'marketProjection': 'EVENT,MARKET_START_TIME,RUNNER_DESCRIPTION', 'eventTypeIds': '7'}
        url = f"{self.BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        data = self.fetcher.get(url, response_type='json', headers={'Accept': 'application/json'})
        if not data or not isinstance(data, dict): self.logger.warning("Invalid response from Betfair"); return []
        races = self._parse_betfair_data(data); self.logger.info(f"Successfully fetched {len(races)} races from Betfair"); return races
    def _parse_betfair_data(self, data: dict) -> List[Race]:
        races = []; event_types = data.get('eventTypes', []);
        if not event_types: return races
        try:
            for event_node in event_types[0].get('eventNodes', []):
                event = event_node.get('event', {})
                for market_node in event_node.get('marketNodes', []):
                    market = market_node.get('market', {})
                    if market.get('marketType', '') != 'WIN': continue
                    runners = [Runner(name=r.get('description', {}).get('runnerName', 'Unknown'), odds=r.get('exchange', {}).get('availableToBack', [{}])[0].get('price')) for r in market_node.get('runners', []) if r.get('state', {}).get('status') == 'ACTIVE']
                    if len(runners) < 3: continue
                    race_number = None
                    event_name = event.get('eventName', '')
                    if 'R' in event_name:
                        try:
                            race_number = int(event_name.split('R')[-1])
                        except (ValueError, IndexError):
                            pass
                    races.append(Race(race_id=f"betfair_{market.get('marketId', 'unknown')}", track_name=event.get('venue', 'Betfair Exchange'), post_time=safe_parse_datetime(market.get('marketStartTime')), race_number=race_number, runners=runners, source=self.SOURCE_ID))
        except Exception as e: self.logger.error(f"Error parsing Betfair data: {e}", exc_info=True)
        return races

class PointsBetAdapter(BaseAdapterV7):
    SOURCE_ID = "pointsbet"; BASE_URL = "https://api.nj.pointsbet.com/api/v2/sports/horse-racing/events/upcoming?page=1"
    def fetch_races(self) -> List[Race]:
        self.logger.info("Fetching from PointsBet"); response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or not isinstance(response_data, dict): self.logger.warning("Invalid response from PointsBet"); return []
        events = response_data.get('events', []);
        if not events: self.logger.warning("No events in PointsBet response"); return []
        races = []
        for event in events:
            try:
                if not event.get('winPlaceOddsAvailable'): continue
                runners = [Runner(name=o.get('name', 'Unknown'), odds=parse_odds_universal(o.get('price'))) for o in event.get('fixedPrice', {}).get('outcomes', []) if o.get('outcomeType') == 'Win']
                if len(runners) < 3: continue
                races.append(Race(race_id=f"pointsbet_{event.get('key', 'unknown')}", track_name=event.get('competitionName', 'Unknown Track'), race_number=event.get('eventNumber'), post_time=safe_parse_datetime(event.get('startsAt')), runners=runners, source=self.SOURCE_ID))
            except Exception as e: self.logger.warning(f"Failed to parse PointsBet event: {e}")
        self.logger.info(f"Successfully fetched {len(races)} races from PointsBet"); return races

# --- RESURRECTED & MODERNIZED LEGACY ADAPTERS ---
class AtTheRacesAdapter(BaseAdapterV7):
    SOURCE_ID = "attheraces"
    def fetch_races(self) -> List[Race]:
        self.logger.info("Fetching from AtTheRaces..."); response_text = self.fetcher.get("https://www.attheraces.com/racecards", response_type='text')
        if not response_text: return []
        soup = BeautifulSoup(response_text, 'lxml'); races = []
        for card in soup.select('.racecard'):
            try:
                track = card.select_one('.track-name').text.strip(); time_str = card.select_one('.race-time').text.strip()
                races.append(Race(race_id=f"atr_{track.replace(' ','')}_{time_str}", track_name=track, post_time=datetime.now(), runners=[], source=self.SOURCE_ID))
            except Exception as e: self.logger.warning(f"Failed to parse ATR card: {e}")
        self.logger.info(f"Found {len(races)} race meetings from ATR."); return races

class RacingAndSportsAdapter(BaseAdapterV7):
    SOURCE_ID = "ras"
    def __init__(self, fetcher: DefensiveFetcher, api_key: Optional[str]): super().__init__(fetcher); self.api_key = api_key
    def fetch_races(self) -> List[Race]:
        if not self.api_key: self.logger.warning("RAS_API_KEY not configured. Skipping."); return []
        self.logger.info("Fetching from RacingAndSports..."); headers = {"X-API-Key": self.api_key}
        meetings = self.fetcher.get("https://api.racingandsports.com.au/Meetings", headers=headers)
        if not meetings or not isinstance(meetings, list): return []
        races = []
        for meeting in meetings[:5]:
            try: races.append(Race(race_id=f"ras_{meeting['MeetingID']}", track_name=meeting.get('TrackName', 'Unknown RAS Track'), post_time=datetime.now(), runners=[], source=self.SOURCE_ID))
            except Exception as e: self.logger.warning(f"Failed to parse RAS meeting: {e}")
        self.logger.info(f"Found {len(races)} race meetings from RAS."); return races

# --- The Ultimate DataSourceOrchestrator ---
class DataSourceOrchestrator:
    def __init__(self):
        self.fetcher = DefensiveFetcher(); self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters: List[BaseAdapterV7] = self._initialize_adapters()
    def _initialize_adapters(self) -> List[BaseAdapterV7]:
        instances = [TVGAdapter(self.fetcher), PointsBetAdapter(self.fetcher), BetfairExchangeAdapter(self.fetcher), AtTheRacesAdapter(self.fetcher), RacingAndSportsAdapter(self.fetcher, api_key=os.getenv("RAS_API_KEY"))]
        self.logger.info(f"Initialized {len(instances)} total adapters for global coverage."); return instances
    def _fetch_from_adapter(self, adapter: BaseAdapterV7) -> tuple[list[Race], dict]:
        adapter_id = adapter.__class__.__name__; start_time = time.time()
        status = {"adapter_id": adapter_id, "timestamp": datetime.now(), "status": "FAILURE", "races_found": 0, "response_time": 0.0, "error_message": None}
        try: races = adapter.fetch_races(); status["status"] = "SUCCESS"; status["races_found"] = len(races); return races, status
        except Exception as e: self.logger.error(f"Adapter {adapter_id} failed: {e}", exc_info=True); status["error_message"] = str(e); return [], status
        finally: status["response_time"] = time.time() - start_time
    def get_races(self) -> tuple[list[Race], list[dict]]:
        self.logger.info(f"Starting concurrent fetch from {len(self.adapters)} adapters..."); all_races, all_statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                try: races, status = future.result(); all_races.extend(races); all_statuses.append(status)
                except Exception as e: self.logger.critical(f"Future for adapter {future_to_adapter[future].__class__.__name__} failed: {e}")
        self.logger.info(f"Concurrent fetch complete. Total races: {len(all_races)}"); return all_races, all_statuses