# python_service/engine.py

import asyncio
import structlog

log = structlog.get_logger(__name__)
import httpx
from datetime import datetime
from typing import Dict, Any, List, Tuple

from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.betfair_greyhound_adapter import BetfairGreyhoundAdapter
from .adapters.racing_and_sports_greyhound_adapter import RacingAndSportsGreyhoundAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.at_the_races_adapter import AtTheRacesAdapter
from .adapters.sporting_life_adapter import SportingLifeAdapter
from .adapters.timeform_adapter import TimeformAdapter
from .adapters.harness_adapter import HarnessAdapter
# from .adapters.greyhound_adapter import GreyhoundAdapter

class OddsEngine:
    def __init__(self, config):
        self.config = config
        self.log = structlog.get_logger(self.__class__.__name__)
        self.adapters: List[BaseAdapter] = [
            BetfairAdapter(config=self.config),
            BetfairGreyhoundAdapter(config=self.config),
            TVGAdapter(config=self.config),
            RacingAndSportsAdapter(config=self.config),
            RacingAndSportsGreyhoundAdapter(config=self.config),
            AtTheRacesAdapter(config=self.config),
            SportingLifeAdapter(config=self.config),
            TimeformAdapter(config=self.config),
            HarnessAdapter(config=self.config)
        ]

        # Conditionally activate the GreyhoundAdapter if its URL is configured
        if self.config.GREYHOUND_API_URL:
            self.log.info("GREYHOUND_API_URL is set. Activating GreyhoundAdapter.")
            self.adapters.append(GreyhoundAdapter(config=self.config))
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
        # Adapters now handle their own exceptions and return a consistent payload.
        # The engine's role is to orchestrate and time the calls.
        result = await adapter.fetch_races(date, self.http_client)
        duration = (datetime.now() - start_time).total_seconds()
        return (adapter.source_name, result, duration)

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
                # This path is taken for exceptions returned by asyncio.gather
                log.error("Adapter fetch failed unexpectedly in gather", error=result, exc_info=False)
                # We cannot know which adapter failed here, so we cannot add a FAILED entry.
                # This is a limitation of the current design, but we prevent a crash.
                continue

            adapter_name, adapter_result, duration = result
            source_info = adapter_result.get('source_info', {})
            source_info['fetch_duration'] = round(duration, 2)
            source_infos.append(source_info)

            if source_info.get('status') == 'SUCCESS':
                all_races.extend(adapter_result.get('races', []))

        return {
            "date": datetime.strptime(date, '%Y-%m-%d').date(),
            "races": all_races,
            "sources": source_infos,
            "metadata": {
                'fetch_time': datetime.now(),
                'sources_queried': [a.source_name for a in target_adapters],
                'sources_successful': len([s for s in source_infos if s['status'] == 'SUCCESS']),
                'sources_failed': len([s for s in source_infos if s['status'] == 'FAILED']),
                'failed_sources_list': [s['name'] for s in source_infos if s['status'] == 'FAILED'],
                'total_races': len(all_races)
            }
        }