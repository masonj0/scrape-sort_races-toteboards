# python_service/engine.py

import asyncio
import structlog
import httpx
from datetime import datetime
from typing import Dict, Any, List, Tuple

from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter
from .adapters.harness_adapter import HarnessAdapter

class OddsEngine:
    def __init__(self, config):
        self.config = config
        self.log = structlog.get_logger(self.__class__.__name__)
        self.adapters: List[BaseAdapter] = [
            BetfairAdapter(config=self.config),
            TVGAdapter(config=self.config),
            RacingAndSportsAdapter(config=self.config),
            PointsBetAdapter(config=self.config),
            HarnessAdapter(config=self.config)
        ]
        self.http_client = httpx.AsyncClient()

    async def close(self):
        await self.http_client.aclose()

    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        """Returns the health status of all registered adapters."""
        statuses = []
        for adapter in self.adapters:
            statuses.append(adapter.get_status())
        return statuses

    async def _time_adapter_fetch(self, adapter: BaseAdapter, date: str) -> Tuple[str, Dict[str, Any], float]:
        """Wraps an adapter's fetch call to accurately measure its duration."""
        start_time = datetime.now()
        try:
            result = await adapter.fetch_races(date, self.http_client)
            duration = (datetime.now() - start_time).total_seconds()
            return (adapter.source_name, result, duration)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log.error("Adapter raised an unhandled exception", adapter=adapter.source_name, error=e)
            # Propagate the exception along with the timing info
            raise e from None

    async def fetch_all_odds(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [self._time_adapter_fetch(adapter, date) for adapter in target_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        source_infos = []
        all_races = []

        for result in results:
            if isinstance(result, Exception):
                # This path is for unexpected errors in the wrapper or adapter itself
                # The adapter name is not easily available here, logging is key
                self.log.error("A fetch task failed unexpectedly", error=result, exc_info=True)
                continue

            adapter_name, adapter_result, fetch_duration = result

            source_infos.append({
                'name': adapter_name,
                'status': adapter_result['source_info']['status'],
                'races_fetched': adapter_result['source_info']['races_fetched'],
                'error_message': adapter_result['source_info']['error_message'],
                'fetch_duration': round(fetch_duration, 2) # Use the accurate, individual duration
            })

            if adapter_result['source_info']['status'] == 'SUCCESS':
                all_races.extend(adapter_result.get('races', []))

        return {
            "date": datetime.strptime(date, '%Y-%m-%d').date(),
            "races": all_races,
            "sources": source_infos,
            "metadata": {
                'fetch_time': datetime.now(),
                'sources_queried': [a.source_name for a in target_adapters],
                'sources_successful': len([s for s in source_infos if s['status'] == 'SUCCESS']),
                'total_races': len(all_races)
            }
        }