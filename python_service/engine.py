# python_service/engine.py

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

class EngineManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters: List[BaseAdapter] = [BetfairAdapter(), TVGAdapter(), RacingAndSportsAdapter(), PointsBetAdapter()]
        self.fetch_interval = 60
        self._last_races: Dict[str, Any] = {}
        self._last_funnel_stats: Dict[str, Any] = {}
        self._last_run_failures: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def fetch_all_races(self) -> None:
        self.logger.info("Starting parallel fetch...")
        tasks = [adapter.fetch_races() for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        async with self._lock:
            all_races, errors, races_by_adapter = [], [], {}
            for i, result in enumerate(results):
                adapter_name = self.adapters[i].__class__.__name__
                if isinstance(result, Exception):
                    errors.append({"adapter": adapter_name, "error": "ExecutionException", "message": str(result)})
                    races_by_adapter[adapter_name] = []
                elif result and result.get('success'):
                    races_by_adapter[adapter_name] = result.get('data', [])
                    all_races.extend(result.get('data', []))
                else:
                    errors.append({"adapter": adapter_name, "error_details": result.get('error_details', {})})
                    races_by_adapter[adapter_name] = []

            self._last_races = {"races": all_races, "timestamp": time.time()}
            self._last_run_failures = errors
            self._last_funnel_stats = {
                'races_fetched_by_source': {name: len(races) for name, races in races_by_adapter.items()},
                'total_races_fetched': sum(len(races) for races in races_by_adapter.values())
            }
            self.logger.info(f"Fetch complete. Races: {len(all_races)}. Errors: {len(errors)}.")

    async def run(self):
        """Blueprint-Enhanced: Intelligent run loop to prevent overlap."""
        while True:
            start_time = time.time()
            try:
                await self.fetch_all_races()
            except asyncio.CancelledError:
                self.logger.info("Engine run loop cancelled.")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in engine loop: {e}", exc_info=True)

            elapsed = time.time() - start_time
            sleep_time = max(0, self.fetch_interval - elapsed)
            if elapsed > self.fetch_interval:
                self.logger.warning(f"Fetch took {elapsed:.2f}s, longer than interval {self.fetch_interval}s. Next fetch will start immediately.")

            await asyncio.sleep(sleep_time)

    async def close_adapters(self):
        for adapter in self.adapters:
            if hasattr(adapter, 'close'): await adapter.close()

    def get_last_races(self): return self._last_races
    def get_funnel_statistics(self): return self._last_funnel_stats
    def get_dashboard_summary(self):
        return {"last_races_summary": self._last_races, "fetcher_failures": self._last_run_failures}