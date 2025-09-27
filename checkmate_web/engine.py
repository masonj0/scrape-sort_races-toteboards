# engine.py
# Upgraded with Historian Schema for Race Results

import logging
import json
import subprocess
import concurrent.futures
from abc import ABC, abstractmethod
from typing import List, Union, Optional, Dict
from datetime import date, datetime, timedelta
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

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

# --- Models ---
class Runner(BaseModel):
    name: str
    odds: Optional[float] = None
    program_number: Optional[int] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    runners: List[Runner]
    source: Optional[str] = None

class HorseSchema(BaseModel):
    name: str
    number: Optional[int] = None
    odds: Optional[float] = None

class RaceDataSchema(BaseModel):
    id: str
    track: str
    raceNumber: Optional[int] = None
    postTime: Optional[str] = None
    horses: List[HorseSchema]

# --- New Historian Schema ---
class RunnerResult(BaseModel):
    name: str
    finishing_position: int
    program_number: Optional[int] = None
    odds: Optional[float] = None

class RaceResult(BaseModel):
    race_id: str
    track_name: str
    race_number: int
    race_date: date
    results: List[RunnerResult]
    source: str

# --- Base Fetcher & Adapters ---
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

            if response_type == 'text':
                return response_text

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logging.warning(f"Failed to decode JSON from {url}")
                return response_text # Return text as fallback
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher
    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError

def _convert_odds_to_float(odds_str: Optional[Union[str, float]]) -> Optional[float]:
    if isinstance(odds_str, float):
        return odds_str
    if not odds_str or not isinstance(odds_str, str):
        return None
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

class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or 'races' not in response_data: return []
        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = [Runner(name=r.get('horseName', 'N/A'), program_number=r.get('programNumber'), odds=self._parse_odds(r.get('odds'))) for r in race_info.get('runners', []) if not r.get('scratched') and self._parse_odds(r.get('odds')) is not None]
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
            event_nodes = data.get('eventTypes', [{}]).get('eventNodes', [])
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
                            if available_to_back: odds = available_to_back.get('price')
                        runners.append(Runner(name=runner.get('description', {}).get('runnerName', 'Unknown'), program_number=runner.get('sortPriority'), odds=odds))
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

# --- Trifecta Analyzer ---
class TrifectaAnalyzer:
    def analyze_race(self, race: RaceDataSchema, settings: Settings) -> dict:
        score = 0
        trifecta_factors = {}
        horses_with_odds = sorted([h for h in race.horses if h.odds], key=lambda h: h.odds)
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

        return {"qualified": score >= settings.QUALIFICATION_SCORE, "checkmateScore": score, "trifectaFactors": trifecta_factors}

# --- Orchestrator ---
PRODUCTION_ADAPTERS = [TVGAdapter, BetfairExchangeAdapter, PointsBetAdapter]

class DataSourceOrchestrator:
    def __init__(self):
        self.fetcher = DefensiveFetcher()
        self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in PRODUCTION_ADAPTERS]

    def _fetch_from_adapter(self, adapter: BaseAdapterV7):
        adapter_id = adapter.__class__.__name__
        try:
            races = adapter.fetch_races()
            notes = f"Successfully parsed {len(races)} races." if races else "No upcoming races found."
            status = {"adapter_id": adapter_id, "status": "OK", "races_found": len(races), "notes": notes, "error_message": None}
            return races, status
        except Exception as e:
            error_message = str(e)
            status = {"adapter_id": adapter_id, "status": "ERROR", "error_message": error_message, "races_found": 0}
            return [], status

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                try:
                    races, status = future.result()
                    if races:
                        all_races.extend(races)
                    statuses.append(status)
                except Exception as e:
                    adapter = future_to_adapter[future]
                    adapter_id = adapter.__class__.__name__
                    statuses.append({"adapter_id": adapter_id, "status": "ERROR", "error_message": str(e), "races_found": 0})
        return all_races, statuses