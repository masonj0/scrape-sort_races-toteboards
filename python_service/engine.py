# python_service/engine.py

import asyncio
import structlog
import httpx
from datetime import datetime
from typing import Dict, Any, List, Tuple

from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.betfair_greyhound_adapter import BetfairGreyhoundAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.racing_and_sports_greyhound_adapter import RacingAndSportsGreyhoundAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter
from .adapters.harness_adapter import HarnessAdapter
from .adapters.at_the_races_adapter import AtTheRacesAdapter
from .adapters.sporting_life_adapter import SportingLifeAdapter
from .adapters.timeform_adapter import TimeformAdapter
# The import for the generic GreyhoundAdapter remains commented out to prevent the bug
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
            PointsBetAdapter(config=self.config),
            HarnessAdapter(config=self.config),
            AtTheRacesAdapter(config=self.config),
            SportingLifeAdapter(config=self.config),
            TimeformAdapter(config=self.config)
        ]
        self.http_client = httpx.AsyncClient()

    async def close(self):
        await self.http_client.aclose()

    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        return [adapter.get_status() for adapter in self.adapters]

    async def _time_adapter_fetch(self, adapter: BaseAdapter, date: str) -> Tuple[str, Dict[str, Any], float]:
        start_time = datetime.now()
        result = await adapter.fetch_races(date, self.http_client)
        duration = (datetime.now() - start_time).total_seconds()
        return (adapter.source_name, result, duration)

    async def fetch_all_odds(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [self._time_adapter_fetch(adapter, date) for adapter in target_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_races = []
        source_infos = []
        for result in results:
            if isinstance(result, Exception):
                self.log.error("A fetch task failed unexpectedly", error=result, exc_info=True)
                continue

            adapter_name, adapter_result, fetch_duration = result
            source_infos.append({
                'name': adapter_name,
                'status': adapter_result['source_info']['status'],
                'races_fetched': adapter_result['source_info']['races_fetched'],
                'error_message': adapter_result['source_info']['error_message'],
                'fetch_duration': round(fetch_duration, 2)
            })

            if adapter_result['source_info']['status'] == 'SUCCESS':
                all_races.extend(adapter_result.get('races', []))

        # De-duplication logic will be re-introduced here in a future, stable mission
        return {
            "date": datetime.strptime(date, '%Y-%m-%d').date(),
            "races": all_races,
            "sources": source_infos
        }