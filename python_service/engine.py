# python_service/engine.py

import asyncio
import structlog
import httpx
from datetime import datetime
from typing import Dict, Any, List, Tuple
from decimal import Decimal
from datetime import timezone

from .models import Race, Runner, OddsData, AggregatedResponse
from .models_v3 import NormalizedRace, NormalizedRunner
from .cache_manager import cache_async_result
from .health import health_monitor
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
from .adapters.betfair_datascientist_adapter import BetfairDataScientistAdapter

log = structlog.get_logger(__name__)

class FortunaEngine:
    def __init__(self, config=None):
        from .config import get_settings
        self.config = config or get_settings()
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
        # V3 ADAPTERS
        self.v3_adapters = [
            BetfairDataScientistAdapter(
                model_name="ThoroughbredModel",
                url="https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kvs-ratings/datasets?id=thoroughbred-model&date="
            )
        ]
        self.http_client = httpx.AsyncClient()

    async def close(self):
        await self.http_client.aclose()

    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        return [adapter.get_status() for adapter in self.adapters]

    async def _time_adapter_fetch(self, adapter: BaseAdapter, date: str) -> Tuple[str, Dict[str, Any], float]:
        """Wraps an adapter's fetch call, catches all exceptions, and returns a consistent payload."""
        start_time = datetime.now()
        try:
            result = await adapter.fetch_races(date, self.http_client)
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_adapter_response(adapter.source_name, success=True, duration=duration)
            return (adapter.source_name, result, duration)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            log.error("Adapter raised an unhandled exception", adapter=adapter.source_name, error=str(e), exc_info=True)
            health_monitor.record_adapter_response(adapter.source_name, success=False, duration=duration)
            failed_result = {
                'races': [],
                'source_info': {
                    'name': adapter.source_name,
                    'status': 'FAILED',
                    'races_fetched': 0,
                    'error_message': str(e),
                    'fetch_duration': duration
                }
            }
            return (adapter.source_name, failed_result, duration)

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

    async def get_races(self, date: str, background_tasks: set, source_filter: str = None) -> Dict[str, Any]:
        if source_filter:
            self.log.info("Bypassing cache for source-specific request", source=source_filter)
            return await self._fetch_races_from_sources(date, source_filter=source_filter)

        return await self._get_all_races_cached(date, background_tasks=background_tasks)

    @cache_async_result(ttl_seconds=300, key_prefix="fortuna_engine_races")
    async def _get_all_races_cached(self, date: str, background_tasks: set) -> Dict[str, Any]:
        """This method fetches races for all sources and its result is cached."""
        self.log.info("CACHE MISS: Fetching all races from sources.", date=date)
        return await self._fetch_races_from_sources(date)

    def _convert_v3_race_to_v2(self, v3_race: NormalizedRace) -> Race:
        """Converts a V3 NormalizedRace object to a V2 Race object."""
        import re
        race_number = 0
        match = re.search(r'\d+', v3_race.race_name)
        if match:
            race_number = int(match.group())

        runners = []
        for v3_runner in v3_race.runners:
            odds_data = OddsData(
                win=Decimal(str(v3_runner.odds_decimal)),
                source=v3_race.source_ids[0],
                last_updated=datetime.now(timezone.utc)
            )
            runner = Runner(
                id=v3_runner.runner_id,
                name=v3_runner.name,
                number=int(v3_runner.saddle_cloth) if v3_runner.saddle_cloth and v3_runner.saddle_cloth.isdigit() else 99,
                odds={v3_race.source_ids[0]: odds_data}
            )
            runners.append(runner)

        return Race(
            id=v3_race.race_key,
            venue=v3_race.track_key,
            race_number=race_number,
            start_time=datetime.fromisoformat(v3_race.start_time_iso),
            runners=runners,
            source=v3_race.source_ids[0],
            race_name=v3_race.race_name
        )

    @cache_async_result(ttl_seconds=300, key_prefix="odds_engine_fetch")
    async def _fetch_races_from_sources(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        """Helper method to contain the logic for fetching and aggregating races."""
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [self._time_adapter_fetch(adapter, date) for adapter in target_adapters]

        # Run V3 (synchronous) adapters in a thread pool
        v3_tasks = [asyncio.to_thread(adapter.fetch_and_normalize) for adapter in self.v3_adapters]

        # Gather results from both V2 (async) and V3 (sync) adapters
        all_tasks = tasks + v3_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        source_infos = []
        all_races = []

        v3_start_time = datetime.now() # Approximate start time for all V3 adapters

        for result in results:
            if isinstance(result, Exception):
                self.log.error("Adapter fetch failed", error=result, exc_info=False)
                continue

            # Correctly differentiate between V2 and V3 results
            if isinstance(result, tuple) and len(result) == 3:  # V2 Adapter Result
                adapter_name, adapter_result, duration = result
                source_info = adapter_result.get('source_info', {})
                source_info['fetch_duration'] = round(duration, 2)
                source_infos.append(source_info)
                if source_info.get('status') == 'SUCCESS':
                    all_races.extend(adapter_result.get('races', []))
            elif isinstance(result, list) and all(isinstance(r, NormalizedRace) for r in result):  # V3 Adapter Result
                if result:
                    v3_races = result
                    adapter_name = v3_races[0].source_ids[0]
                    translated_races = [self._translate_v3_race_to_v2(nr) for nr in result]
                    all_races.extend(translated_races)

                    v3_duration = (datetime.now() - v3_start_time).total_seconds()
                    source_infos.append({
                        'name': adapter_name,
                        'status': 'SUCCESS',
                        'races_fetched': len(translated_races),
                        'error_message': None,
                        'fetch_duration': round(v3_duration, 2)
                    })

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

        # --- Windows Operator Experience Enhancement ---
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                "Fortuna Faucet",
                f"Initial data load complete. {len(deduped_races)} races are ready for analysis.",
                duration=10,
                threaded=True
            )
        except (ImportError, RuntimeError):
            # Fails gracefully if not on Windows or library is missing
            pass

        return response_obj.model_dump()


    def _translate_v3_race_to_v2(self, norm_race: NormalizedRace) -> Race:
        """Translates a V3 NormalizedRace into a V2 Race object."""
        runners = []
        for norm_runner in norm_race.runners:
            adapter_name = norm_race.source_ids[0] if norm_race.source_ids else "UnknownV3"
            odds_data = OddsData(
                win=Decimal(str(norm_runner.odds_decimal)),
                source=adapter_name,
                last_updated=datetime.now(timezone.utc)
            )

            try:
                runner_number = int(norm_runner.saddle_cloth)
            except (ValueError, TypeError):
                runner_number = None

            runner = Runner(
                id=norm_runner.runner_id,
                name=norm_runner.name,
                number=runner_number,
                odds={adapter_name: odds_data}
            )
            runners.append(runner)

        return Race(
            id=norm_race.race_key,
            venue=norm_race.track_key,
            start_time=datetime.fromisoformat(norm_race.start_time_iso),
            race_number=0, # V3 model does not have race_number, placeholder
            runners=runners,
            source=norm_race.source_ids[0] if norm_race.source_ids else "UnknownV3",
            # Store extra V3 data in metadata for future use
            metadata={"v3_race_name": norm_race.race_name}
        )
