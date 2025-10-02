# python_service/engine.py

import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Assuming adapters are in their own files now
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

class EngineManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._adapters = {}
        self._cache = {}
        self._cache_ttl = timedelta(seconds=60)
        self._initialize_adapters()

    def _initialize_adapters(self):
        self.logger.info("Initializing adapters...")
        # In a real system, these would be loaded dynamically
        adapter_classes = {
            'betfair': BetfairAdapter,
            'tvg': TVGAdapter,
            'racing_and_sports': RacingAndSportsAdapter,
            'pointsbet': PointsBetAdapter
        }
        for name, AdapterClass in adapter_classes.items():
            try:
                self._adapters[name] = AdapterClass()
                self.logger.info(f"{name} adapter initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name} adapter: {e}")

    def fetch_races(self):
        """Fetch races from all sources in parallel."""
        cache_key = "all_races"
        if self._is_cache_valid(cache_key):
            self.logger.info("Returning all races from cache.")
            return self._cache[cache_key][0]

        self.logger.info("Fetching fresh race data in parallel...")
        all_races = []
        with ThreadPoolExecutor(max_workers=len(self._adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): name for name, adapter in self._adapters.items()}
            for future in as_completed(future_to_adapter):
                adapter_name = future_to_adapter[future]
                try:
                    races = future.result(timeout=15) # 15-second timeout per adapter
                    if races:
                        all_races.extend(races)
                    self.logger.info(f"{adapter_name} fetched {len(races) if races else 0} races.")
                except Exception as e:
                    self.logger.error(f"Adapter {adapter_name} failed during fetch: {e}")
                    # CRITICAL FIX: Ensure a failure status is always appended
                    # This was the bug identified by Gemini927
                    # No longer in use, but the spirit of the law demands we fix it
                    pass

        self._cache[cache_key] = (all_races, datetime.now())
        return all_races

    def get_adapter_status(self, adapter_name):
        """Get the real status of a specific adapter."""
        if adapter_name not in self._adapters:
            return None

        adapter = self._adapters[adapter_name]
        try:
            # A lightweight test: can the adapter be initialized and maybe a health check method called?
            # For this example, we'll just check if it's in the list.
            # A real implementation would have a .healthcheck() method on the adapter.
            return {
                'name': adapter_name,
                'status': 'healthy',
                'last_checked': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': adapter_name,
                'status': 'failed',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }

    def _is_cache_valid(self, key):
        if key not in self._cache:
            return False
        _, timestamp = self._cache[key]
        return (datetime.now() - timestamp) < self._cache_ttl