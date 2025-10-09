# python_service/engine.py

import asyncio
import structlog
import httpx
import json
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, Any, List, Tuple

from .models import Race, AggregatedResponse
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
from .adapters.the_racing_api_adapter import TheRacingApiAdapter
from .adapters.gbgb_api_adapter import GbgbApiAdapter

log = structlog.get_logger(__name__)

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
            TheRacingApiAdapter(config=self.config),
            GbgbApiAdapter(config=self.config),
            HarnessAdapter(config=self.config)
        ]
        self.http_client = httpx.AsyncClient()
        self.redis_client = redis.from_url(self.config.REDIS_URL, decode_responses=True)
        self.log.info("Redis client initialized", redis_url=self.config.REDIS_URL)

    async def close(self):
        await self.http_client.aclose()
        await self.redis_client.close()

    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        return [adapter.get_status() for adapter in self.adapters]

    async def _time_adapter_fetch(self, adapter: BaseAdapter, date: str) -> Tuple[str, Dict[str, Any], float]:
        start_time = datetime.now()
        result = await adapter.fetch_races(date, self.http_client)
        duration = (datetime.now() - start_time).total_seconds()
        return (adapter.source_name, result, duration)

    def _race_key(self, race: Race) -> str:
        return f"{race.venue.lower().strip()}|{race.race_number}|{race.start_time.strftime('%H:%M')}"

    def _dedupe_races(self, races: List[Race]) -> List[Race]:
        race_map: Dict[str, Race] = {}
        for race in races:
            key = self._race_key(race)
            if key not in race_map:
                race_map[key] = race
            else:
                existing_race = race_map[key]
                runner_map = {r.number: r for r in existing_race.runners}
                for new_runner in race.runners:
                    if new_runner.number in runner_map:
                        runner_map[new_runner.number].odds.update(new_runner.odds)
                    else:
                        existing_race.runners.append(new_runner)
        return list(race_map.values())

    async def fetch_all_odds(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        cache_key = f"fortuna:races:{date}"
        if not source_filter: # Only use cache for 'all sources' requests
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    self.log.info("CACHE HIT", key=cache_key)
                    # Pydantic can validate directly from the JSON string
                    return AggregatedResponse.model_validate_json(cached_data).model_dump()
            except Exception as e:
                self.log.error("Redis GET failed", error=str(e))

        self.log.info("CACHE MISS", key=cache_key)
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [self._time_adapter_fetch(adapter, date) for adapter in target_adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        source_infos = []
        all_races = []
        for result in results:
            if isinstance(result, Exception):
                self.log.error("Adapter fetch failed", error=result, exc_info=False)
                continue
            adapter_name, adapter_result, duration = result
            source_info = adapter_result.get('source_info', {})
            source_info['fetch_duration'] = round(duration, 2)
            source_infos.append(source_info)
            if source_info.get('status') == 'SUCCESS':
                all_races.extend(adapter_result.get('races', []))

        deduped_races = self._dedupe_races(all_races)

        response_obj = AggregatedResponse(
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            races=deduped_races,
            sources=source_infos,
            metadata={
                'fetch_time': datetime.now(),
                'sources_queried': [a.source_name for a in target_adapters],
                'sources_successful': len([s for s in source_infos if s['status'] == 'SUCCESS']),
                'total_races': len(deduped_races)
            }
        )

        if not source_filter: # Only set cache for 'all sources' requests
            try:
                # Cache the result for 5 minutes (300 seconds)
                await self.redis_client.set(cache_key, response_obj.model_dump_json(), ex=300)
                self.log.info("CACHE SET", key=cache_key, expiry=300)
            except Exception as e:
                self.log.error("Redis SET failed", error=str(e))

        return response_obj.model_dump()