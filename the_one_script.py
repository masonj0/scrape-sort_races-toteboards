#!/usr/bin/env python3
"""
# The Sovereign Script (Diagnostic V9)
# A single, self-contained artifact for diagnostics and demonstration of the complete Python data pipeline.
"""

import logging
import json
import subprocess
import concurrent.futures
import time
import sqlite3
from collections import defaultdict
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict
from datetime import datetime
import configparser
from pydantic import BaseModel, Field
from cachetools import TTLCache

# --- 1. MODELS ---

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

# --- 2. DATABASE HANDLER ---

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def _setup_database(self):
        schema = """
        CREATE TABLE IF NOT EXISTS live_races (
            race_id TEXT PRIMARY KEY,
            track_name TEXT NOT NULL,
            race_number INTEGER,
            post_time DATETIME,
            raw_data_json TEXT,
            checkmate_score REAL NOT NULL,
            qualified BOOLEAN NOT NULL,
            trifecta_factors_json TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_races_qualified_score ON live_races(qualified, checkmate_score DESC);
        """
        try:
            with self._get_connection() as conn:
                conn.executescript(schema)
                conn.commit()
            self.logger.info("Database schema created successfully")
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            raise

    def update_races(self, races: List[Race]):
        if not races:
            self.logger.warning("No races to update")
            return
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for race in races:
                    cursor.execute("INSERT OR REPLACE INTO live_races (race_id, track_name, race_number, post_time, raw_data_json, checkmate_score, qualified, trifecta_factors_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (race.race_id, race.track_name, race.race_number, race.post_time, race.model_dump_json(), race.checkmate_score or 0, race.is_qualified or False, race.trifecta_factors_json, datetime.now()))
                conn.commit()
            self.logger.info(f"Successfully updated {len(races)} races in database")
        except Exception as e:
            self.logger.error(f"Database update failed: {e}")
            raise

# --- 3. CORE ENGINE ---

class DefensiveFetcher:
    def __init__(self, max_retries=3, initial_backoff=1):
        self._max_retries = max_retries
        self._initial_backoff = initial_backoff
        self._circuit_breaker = defaultdict(lambda: {'failures': 0, 'is_open': False, 'open_until': 0})

    def _is_breaker_open(self, domain):
        breaker = self._circuit_breaker[domain]
        if breaker['is_open'] and time.time() < breaker['open_until']:
            return True
        elif breaker['is_open']: # Reset if timeout has passed
            breaker['is_open'] = False
            breaker['failures'] = 0
        return False

    def _trip_breaker(self, domain):
        breaker = self._circuit_breaker[domain]
        breaker['failures'] += 1
        if breaker['failures'] >= 5: # Trip after 5 consecutive failures
            breaker['is_open'] = True
            breaker['open_until'] = time.time() + 60 # Open for 60 seconds

    def get(self, url, headers=None, timeout=15):
        domain = url.split('/')[2]
        if self._is_breaker_open(domain):
            print(f"[WARN] Circuit breaker is open for {domain}. Skipping request.")
            return None

        for attempt in range(self._max_retries):
            try:
                command = ["curl", "-s", "-L", "--max-time", str(timeout)]
                if headers:
                    for key, value in headers.items():
                        command.extend(["-H", f"{key}: {value}"])
                command.append(url)

                result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)
                # Reset failure count on success
                self._circuit_breaker[domain]['failures'] = 0
                return json.loads(result.stdout) # Assuming JSON response
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
                print(f"[ERROR] Attempt {attempt + 1} for {url} failed: {e}")
                if attempt == self._max_retries - 1: # Last attempt
                    self._trip_breaker(domain)
                    return None
                time.sleep(self._initial_backoff * (2 ** attempt)) # Exponential backoff
        return None

class BaseAdapterV8(ABC):
    def __init__(self, fetcher: DefensiveFetcher, config):
        self.fetcher, self.config = fetcher, config
        self.cache = TTLCache(maxsize=100, ttl=300)
        self.logger = logging.getLogger(self.__class__.__name__)
    @abstractmethod
    def fetch_races(self) -> List[Race]: raise NotImplementedError

class EnhancedTVGAdapter(BaseAdapterV8):
    NAME = "TVG"
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        cache_key = f"tvg_races_{datetime.now().hour}"
        if cache_key in self.cache: return self.cache[cache_key]

        response_data = self.fetcher.get(self.BASE_URL)
        if not response_data or 'races' not in response_data: return []
        
        validated_races = []
        for race_data in response_data.get('races', []):
            try:
                transformed_runners = []
                for r in race_data.get('runners', []):
                    if not r.get('scratched') and r.get('odds'):
                        odds = self._parse_odds(r.get('odds'))
                        if odds:
                            transformed_runners.append({
                                'name': r.get('horseName', 'N/A'),
                                'odds': odds
                            })

                if len(transformed_runners) < 3:
                    continue

                transformed_race = {
                    'race_id': f"tvg_{race_data.get('raceId')}",
                    'track_name': race_data.get('trackName', 'N/A'),
                    'race_number': race_data.get('raceNumber'),
                    'post_time': self._parse_datetime(race_data.get('postTime')),
                    'runners': transformed_runners,
                    'source': self.SOURCE_ID
                }
                validated_races.append(Race.parse_obj(transformed_race))
            except Exception as e:
                self.logger.warning(f"[VALIDATION_ERROR] Skipping malformed TVG race: {e}")

        self.cache[cache_key] = validated_races
        return validated_races
    def _parse_odds(self, odds_data) -> Optional[float]:
        if not odds_data or odds_data.get('morningLine') is None: return None
        try: num, den = map(int, odds_data['morningLine'].split('/')); return (num / den) + 1.0
        except (ValueError, TypeError, ZeroDivisionError): return None
    def _parse_datetime(self, time_str) -> Optional[datetime]:
        if not time_str: return None
        try: return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except: return None

class EnhancedBetfairAdapter(BaseAdapterV8):
    NAME = "Betfair"
    SOURCE_ID = "betfair_exchange"
    BASE_URL = "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?alt=json&filter=canonical&maxResults=10&eventTypeIds=7"
    def fetch_races(self) -> List[Race]:
        data = self.fetcher.get(self.BASE_URL, headers={'Accept': 'application/json'})
        if not data: return []

        validated_races = []
        try:
            event_nodes = data.get('eventTypes', [{}])[0].get('eventNodes', [])
            for event_node in event_nodes[:3]:
                event = event_node.get('event', {})
                for market_node in event_node.get('marketNodes', []):
                    market = market_node.get('market', {})
                    if market.get('marketType') != 'WIN': continue

                    transformed_runners = []
                    for runner in market_node.get('runners', []):
                        if runner.get('state', {}).get('status') == 'ACTIVE':
                            odds = None
                            if 'exchange' in runner:
                                available_to_back = runner['exchange'].get('availableToBack', [])
                                if available_to_back: odds = available_to_back[0].get('price')
                            if odds:
                                transformed_runners.append({
                                    'name': runner.get('description', {}).get('runnerName', 'Unknown'),
                                    'odds': odds
                                })

                    if len(transformed_runners) >= 3:
                        try:
                            transformed_race = {
                                'race_id': f"betfair_{market.get('marketId', 'unknown')}",
                                'track_name': event.get('venue', 'Betfair Exchange'),
                                'runners': transformed_runners,
                                'source': self.SOURCE_ID
                                # Note: Betfair API doesn't provide race_number or post_time in this endpoint
                            }
                            validated_races.append(Race.parse_obj(transformed_race))
                        except Exception as e:
                            self.logger.warning(f"[VALIDATION_ERROR] Skipping malformed Betfair race: {e}")

        except Exception as e:
            self.logger.error(f"Error parsing Betfair data: {e}")
            
        return validated_races

PRODUCTION_ADAPTERS = [EnhancedTVGAdapter, EnhancedBetfairAdapter]

class SuperchargedOrchestrator:
    def __init__(self, config):
        self.fetcher = DefensiveFetcher()
        self.config = config
        self.adapters = [Adapter(self.fetcher, self.config) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_races_parallel(self) -> List[Race]:
        all_races = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): adapter for adapter in self.adapters}

            for future in concurrent.futures.as_completed(future_to_adapter):
                adapter = future_to_adapter[future]
                try:
                    races = future.result()
                    if races:
                        self.logger.info(f"Adapter '{adapter.NAME}' successfully fetched {len(races)} races.")
                        all_races.extend(races)
                    else:
                        self.logger.warning(f"Adapter '{adapter.NAME}' returned no races.")
                except Exception as e:
                    self.logger.critical(f"Adapter '{adapter.NAME}' failed during execution: {e}", exc_info=True)

        return self._post_process(all_races)

    def _post_process(self, races: List[Race]) -> List[Race]:
        # Deduplicate races based on a unique identifier
        processed = {race.race_id: race for race in races}.values()
        return list(processed)

class EnhancedTrifectaAnalyzer:
    def __init__(self, config):
        self.config = config['analysis']

    def analyze_race(self, race: Race) -> Race:
        score, factors = 0.0, {}
        horses_with_odds = sorted([r for r in race.runners if r.odds], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)

        # Get values from config
        field_size_optimal_min = self.config.getint('field_size_optimal_min')
        field_size_optimal_max = self.config.getint('field_size_optimal_max')
        field_size_acceptable_min = self.config.getint('field_size_acceptable_min')
        field_size_acceptable_max = self.config.getint('field_size_acceptable_max')
        field_size_optimal_points = self.config.getfloat('field_size_optimal_points')
        field_size_acceptable_points = self.config.getfloat('field_size_acceptable_points')
        field_size_penalty_points = self.config.getfloat('field_size_penalty_points')
        max_fav_odds = self.config.getfloat('max_fav_odds')
        fav_odds_points = self.config.getfloat('fav_odds_points')
        min_2nd_fav_odds = self.config.getfloat('min_2nd_fav_odds')
        second_fav_odds_points = self.config.getfloat('second_fav_odds_points')
        qualification_score = self.config.getfloat('qualification_score')

        if field_size_optimal_min <= num_runners <= field_size_optimal_max: p, ok, r = field_size_optimal_points, True, f"Optimal field size ({num_runners})"
        elif field_size_acceptable_min <= num_runners <= field_size_acceptable_max: p, ok, r = field_size_acceptable_points, True, f"Acceptable field size ({num_runners})"
        else: p, ok, r = field_size_penalty_points, False, f"Field size not ideal ({num_runners})"
        score += p; factors["fieldSize"] = {"points": p, "ok": ok, "reason": r}

        if num_runners >= 2:
            fav, sec_fav = horses_with_odds[0], horses_with_odds[1]
            if fav.odds <= max_fav_odds: p, ok, r = fav_odds_points, True, f"Favorite odds OK ({fav.odds:.2f})"
            else: p, ok, r = 0, False, f"Favorite odds too high ({fav.odds:.2f})"
            score += p; factors["favoriteOdds"] = {"points": p, "ok": ok, "reason": r}
            if sec_fav.odds >= min_2nd_fav_odds: p, ok, r = second_fav_odds_points, True, f"2nd Favorite OK ({sec_fav.odds:.2f})"
            else: p, ok, r = 0, False, f"2nd Favorite odds too low ({sec_fav.odds:.2f})"
            score += p; factors["secondFavoriteOdds"] = {"points": p, "ok": ok, "reason": r}

        race.checkmate_score = score
        race.is_qualified = score >= qualification_score
        race.trifecta_factors_json = json.dumps(factors)
        return race

# --- 4. MAIN EXECUTION BLOCK ---

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