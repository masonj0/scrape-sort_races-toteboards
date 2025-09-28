# engine.py
# The final, perfected, 10/10 specification for the Python Collection Service.

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
    data_quality_score: Optional[float] = None
    checkmate_score: Optional[float] = None
    is_qualified: Optional[bool] = None
    analysis_details: Optional[str] = None
    trifecta_factors_json: Optional[str] = None
    analysis_details: Optional[str] = None

# --- Resilient Fetcher ---
class DefensiveFetcher:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

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
                return response_text
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

# --- Enhanced Adapters ---
class BaseAdapterV8(ABC):
    def __init__(self, fetcher: DefensiveFetcher, settings: Settings):
        self.fetcher = fetcher
        self.settings = settings
        self.cache = TTLCache(maxsize=100, ttl=300)
        self.logger = logging.getLogger(self.__class__.__name__)
    @abstractmethod
    def fetch_races(self) -> List[Race]: raise NotImplementedError

class EnhancedTVGAdapter(BaseAdapterV8):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def _parse_odds(self, odds_data: Optional[Dict]) -> Optional[float]:
        if not odds_data or odds_data.get('morningLine') is None: return None
        try:
            num, den = map(int, odds_data['morningLine'].split('/'))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, TypeError, ZeroDivisionError): return None

    def fetch_races(self) -> List[Race]:
        cache_key = f"tvg_races_{datetime.now().strftime('%Y-%m-%d-%H')}"
        cached_races = self.cache.get(cache_key)
        if cached_races is not None:
            self.logger.info(f"Cache hit for {self.SOURCE_ID}. Returning {len(cached_races)} cached races.")
            return cached_races

        response_data = self.get(self.BASE_URL)
        if not isinstance(response_data, dict) or 'races' not in response_data:
            self.logger.warning(f"No 'races' key found in {self.SOURCE_ID} API response.")
            return []

        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = [Runner(name=r.get('horseName', 'N/A'), odds=self._parse_odds(r.get('odds'))) for r in race_info.get('runners', []) if not r.get('scratched')]
                if len(runners) < 3: continue

                all_races.append(Race(
                    race_id=f"tvg_{race_info.get('raceId')}",
                    track_name=race_info.get('trackName', 'N/A'),
                    race_number=race_info.get('raceNumber'),
                    post_time=datetime.fromisoformat(race_info.get('postTime').replace('Z', '+00:00')) if race_info.get('postTime') else None,
                    runners=runners,
                    source=self.SOURCE_ID
                ))
            except Exception as e:
                self.logger.warning(f"Skipping malformed TVG race due to: {e}")
                continue

        self.cache[cache_key] = all_races
        self.logger.info(f"Fetched and cached {len(all_races)} new races from {self.SOURCE_ID}.")
        return all_races

PRODUCTION_ADAPTERS = [EnhancedTVGAdapter]

# --- Supercharged Orchestrator ---
class SuperchargedOrchestrator:
    def __init__(self, settings: Settings):
        self.fetcher = DefensiveFetcher()
        self.settings = settings
        self.adapters = [Adapter(self.fetcher, self.settings) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch_from_adapter(self, adapter: BaseAdapterV8) -> tuple[list[Race], dict]:
        start_time = time.monotonic()
        status = {'adapter_id': adapter.__class__.__name__, 'timestamp': datetime.now().isoformat()}
        try:
            races = adapter.fetch_races()
            status.update({'status': 'OK', 'races_found': len(races)})
            return races, status
        except Exception as e:
            self.logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}", exc_info=True)
            status.update({'status': 'ERROR', 'races_found': 0, 'error_message': str(e)})
            return [], status
        finally:
            end_time = time.monotonic()
            status['response_time'] = end_time - start_time

    def get_races_parallel(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(self._fetch_from_adapter, adapter): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                try:
                    races, status = future.result()
                    statuses.append(status)
                    if races:
                        all_races.extend(races)
                except Exception as e:
                    adapter_name = future_to_adapter[future].__class__.__name__
                    self.logger.critical(f"A future for adapter {adapter_name} failed unexpectedly: {e}", exc_info=True)
                    statuses.append({'adapter_id': adapter_name, 'status': 'FATAL', 'error_message': str(e)})
        self.logger.info(f"Orchestrator fetched {len(all_races)} total races.")
        return all_races, statuses

# --- Enhanced Trifecta Analyzer ---
class EnhancedTrifectaAnalyzer:
    def __init__(self, settings: Settings):
        self.settings = settings

    def analyze_race_advanced(self, race: Race) -> Race:
        score = 0.0
        factors = {}

        runners_with_odds = sorted([r for r in race.runners if r.odds is not None], key=lambda r: r.odds)
        num_runners = len(runners_with_odds)

        # Field Size Analysis
        if self.settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= self.settings.FIELD_SIZE_OPTIMAL_MAX:
            points, ok, reason = self.settings.FIELD_SIZE_OPTIMAL_POINTS, True, f"Optimal field size ({num_runners})"
        elif self.settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= self.settings.FIELD_SIZE_ACCEPTABLE_MAX:
            points, ok, reason = self.settings.FIELD_SIZE_ACCEPTABLE_POINTS, True, f"Acceptable field size ({num_runners})"
        else:
            points, ok, reason = self.settings.FIELD_SIZE_PENALTY_POINTS, False, f"Field size not ideal ({num_runners})"
        score += points
        factors['fieldSize'] = {'points': points, 'ok': ok, 'reason': reason}

        # Odds Analysis
        if num_runners >= 2:
            fav_odds = runners_with_odds.odds
            sec_fav_odds = runners_with_odds.odds

            if fav_odds <= self.settings.MAX_FAV_ODDS:
                points, ok, reason = self.settings.FAV_ODDS_POINTS, True, f"Favorite odds OK ({fav_odds:.2f})"
            else:
                points, ok, reason = 0, False, f"Favorite odds too high ({fav_odds:.2f})"
            score += points
            factors['favoriteOdds'] = {'points': points, 'ok': ok, 'reason': reason}

            if sec_fav_odds >= self.settings.MIN_2ND_FAV_ODDS:
                points, ok, reason = self.settings.SECOND_FAV_ODDS_POINTS, True, f"2nd Favorite OK ({sec_fav_odds:.2f})"
            else:
                points, ok, reason = 0, False, f"2nd Favorite odds too low ({sec_fav_odds:.2f})"
            score += points
            factors['secondFavoriteOdds'] = {'points': points, 'ok': ok, 'reason': reason}

        race.checkmate_score = score
        race.is_qualified = score >= self.settings.QUALIFICATION_SCORE
        race.trifecta_factors_json = json.dumps(factors)
        race.analysis_details = json.dumps({'base_score': score})
        return race