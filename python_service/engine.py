# python_service/engine.py

import asyncio
import logging
import httpx
from datetime import datetime
from typing import Dict, Any, List

from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

class OddsEngine:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters: List[BaseAdapter] = [
            BetfairAdapter(), TVGAdapter(),
            RacingAndSportsAdapter(), PointsBetAdapter()
        ]
        self.http_client = httpx.AsyncClient()

    async def close(self):
        await self.http_client.aclose()

    async def fetch_all_odds(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [adapter.fetch_races(date, self.http_client) for adapter in target_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        source_infos = []
        start_time = datetime.now()

        for i, result in enumerate(results):
            adapter_name = target_adapters[i].source_name
            fetch_duration = (datetime.now() - start_time).total_seconds() # Simplified duration

            if isinstance(result, Exception):
                source_infos.append({
                    'name': adapter_name, 'status': 'FAILED',
                    'races_fetched': 0, 'error_message': str(result), 'fetch_duration': fetch_duration
                })
            else:
                successful_results.append(result)
                source_infos.append({
                    'name': adapter_name, 'status': 'SUCCESS',
                    'races_fetched': len(result.get('races', [])),
                    'error_message': None, 'fetch_duration': fetch_duration
                })

        all_races = []
        for res in successful_results:
            all_races.extend(res.get('races', []))

        # In a future step, this will call a NormalizeAndDeduplicate function
        # For now, we return the raw aggregation

        return {
            "date": datetime.strptime(date, '%Y-%m-%d').date(),
            "races": all_races,
            "sources": source_infos,
            "metadata": {
                'fetch_time': datetime.now(),
                'sources_queried': [a.source_name for a in target_adapters],
                'sources_successful': len(successful_results),
                'total_races': len(all_races)
            }
        }