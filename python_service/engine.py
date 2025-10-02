# python_service/engine.py

import logging
import time
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

# NEW: DefensiveFetcher with resilience patterns
class DefensiveFetcher:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self._rate_limiters: Dict[str, float] = {}

    def get(self, url: str, headers: dict, source_id: str, timeout: int = 15):
        # 1. Circuit Breaker Check
        if self._is_circuit_open(source_id):
            self.logger.warning(f"Circuit for {source_id} is open. Skipping request.")
            return None

        # 2. Rate Limiting Check
        self._apply_rate_limit(source_id)

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            self._record_success(source_id)
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Fetch failed for {source_id}: {e}")
            self._record_failure(source_id)
            return None

    def post(self, url: str, headers: dict, data: Any, source_id: str, timeout: int = 10):
        if self._is_circuit_open(source_id):
            self.logger.warning(f"Circuit for {source_id} is open. Skipping request.")
            return None
        self._apply_rate_limit(source_id)
        try:
            response = requests.post(url, headers=headers, data=data, timeout=timeout)
            response.raise_for_status()
            self._record_success(source_id)
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"POST fetch failed for {source_id}: {e}")
            self._record_failure(source_id)
            return None

    def _is_circuit_open(self, source_id: str) -> bool:
        breaker = self._circuit_breakers.get(source_id, {'failures': 0, 'open_until': 0})
        if time.time() < breaker['open_until']:
            return True
        return False

    def _record_failure(self, source_id: str):
        breaker = self._circuit_breakers.setdefault(source_id, {'failures': 0, 'open_until': 0})
        breaker['failures'] += 1
        if breaker['failures'] >= 3:
            breaker['open_until'] = time.time() + 60  # Open for 60 seconds
            self.logger.warning(f"Circuit breaker for {source_id} has been opened.")

    def _record_success(self, source_id: str):
        self._circuit_breakers.pop(source_id, None) # Reset on success

    def _apply_rate_limit(self, source_id: str, delay: float = 1.0):
        last_call = self._rate_limiters.get(source_id, 0)
        elapsed = time.time() - last_call
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._rate_limiters[source_id] = time.time()


class EngineManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fetcher = DefensiveFetcher() # Use the new hardened fetcher
        self._adapters = {}
        self._cache = {}
        self._cache_ttl = timedelta(seconds=60)
        self._initialize_adapters()

    def _initialize_adapters(self):
        # Adapters will now receive the shared fetcher instance
        adapter_classes = {
            'betfair': BetfairAdapter,
            'tvg': TVGAdapter,
            'racing_and_sports': RacingAndSportsAdapter,
            'pointsbet': PointsBetAdapter
        }
        for name, AdapterClass in adapter_classes.items():
            try:
                self._adapters[name] = AdapterClass(self.fetcher)
                self.logger.info(f"{name} adapter initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name} adapter: {e}")

    def fetch_races(self):
        cache_key = "all_races"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key][0]

        all_races = []
        with ThreadPoolExecutor(max_workers=len(self._adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): name for name, adapter in self._adapters.items()}
            for future in as_completed(future_to_adapter):
                adapter_name = future_to_adapter[future]
                try:
                    races = future.result(timeout=20)
                    if races:
                        all_races.extend(races)
                except Exception as e:
                    self.logger.error(f"Adapter {adapter_name} failed during fetch: {e}")

        self._cache[cache_key] = (all_races, datetime.now())
        return all_races

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Provides a high-level summary of the last fetched data."""
        cache_key = "all_races"
        if not self._is_cache_valid(cache_key):
            # Return a message indicating data is being fetched if cache is cold
            return {"status": "stale", "message": "Data is being fetched. Please try again shortly."}

        races, timestamp = self._cache[cache_key]
        sources = set(race.source for race in races)
        total_runners = sum(len(race.runners) for race in races)

        return {
            "status": "ok",
            "last_updated": timestamp.isoformat(),
            "cache_expires_in_seconds": int(self._cache_ttl.total_seconds() - (datetime.now() - timestamp).total_seconds()),
            "total_races": len(races),
            "total_runners": total_runners,
            "active_sources": list(sources)
        }

    def get_adapter_status(self, adapter_name):
        # This can be enhanced further to check the circuit breaker status
        if adapter_name not in self._adapters:
            return None
        return {
            'name': adapter_name,
            'status': 'healthy' if not self.fetcher._is_circuit_open(adapter_name) else 'degraded',
            'last_checked': datetime.now().isoformat()
        }

    def _is_cache_valid(self, key):
        if key not in self._cache:
            return False
        _, timestamp = self._cache[key]
        return (datetime.now() - timestamp) < self._cache_ttl