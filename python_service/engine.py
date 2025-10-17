# python_service/engine.py

import asyncio
import inspect
from datetime import datetime
from datetime import timezone
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import asyncio
import httpx
import structlog

from .adapters.at_the_races_adapter import AtTheRacesAdapter
from .adapters.base import BaseAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.betfair_datascientist_adapter import BetfairDataScientistAdapter
from .adapters.betfair_greyhound_adapter import BetfairGreyhoundAdapter
from .adapters.equibase_adapter import EquibaseAdapter
from .adapters.gbgb_api_adapter import GbgbApiAdapter
from .adapters.harness_adapter import HarnessAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.racing_and_sports_greyhound_adapter import RacingAndSportsGreyhoundAdapter
from .adapters.racingpost_adapter import RacingPostAdapter
from .adapters.sporting_life_adapter import SportingLifeAdapter
from .adapters.the_racing_api_adapter import TheRacingApiAdapter
from .adapters.timeform_adapter import TimeformAdapter
from .adapters.tvg_adapter import TVGAdapter
from .cache_manager import cache_async_result
from .health import health_monitor
from .models import AggregatedResponse
from .models import OddsData
from .models import Race
from .models import Runner
from .models_v3 import NormalizedRace

log = structlog.get_logger(__name__)


class FortunaEngine:
    def __init__(self, config=None):
        from .config import get_settings

        self.config = config or get_settings()
        self.logger = structlog.get_logger(__name__)
        self.adapters: List[BaseAdapter] = [
            BetfairAdapter(source_name=BetfairAdapter.SOURCE_NAME, base_url=BetfairAdapter.BASE_URL),
            BetfairGreyhoundAdapter(source_name=BetfairGreyhoundAdapter.SOURCE_NAME, base_url=BetfairGreyhoundAdapter.BASE_URL),
            RacingAndSportsAdapter(config=self.config),
            RacingAndSportsGreyhoundAdapter(config=self.config),
            AtTheRacesAdapter(config=self.config),
            RacingPostAdapter(config=self.config),
            HarnessAdapter(config=self.config),
            EquibaseAdapter(config=self.config),
            SportingLifeAdapter(config=self.config),
            TimeformAdapter(config=self.config),
            TheRacingApiAdapter(config=self.config),
            GbgbApiAdapter(config=self.config),
        ]
        # V3 ADAPTERS
        self.v3_adapters = [
            BetfairDataScientistAdapter(
                model_name="ThoroughbredModel",
                url="https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kvs-ratings/datasets?id=thoroughbred-model&date=",
            ),
            TVGAdapter(config=self.config),
        ]
        self.http_limits = httpx.Limits(
            max_connections=config.HTTP_POOL_CONNECTIONS, max_keepalive_connections=config.HTTP_MAX_KEEPALIVE
        )
        self.http_client = httpx.AsyncClient(limits=self.http_limits, http2=True)

    async def close(self):
        await self.http_client.aclose()

    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        return [adapter.get_status() for adapter in self.adapters]

    async def _time_adapter_fetch(self, adapter: BaseAdapter, date: str) -> Tuple[str, Dict[str, Any], float]:
        """
        Wraps an adapter's fetch call for safe, non-blocking execution,
        and returns a consistent payload with timing information.
        Handles both modern async adapters and legacy sync adapters.
        """
        start_time = datetime.now()
        races = []
        error_message = None
        is_success = False

        try:
            # Check if the adapter's fetch_races method is a modern async function
            if inspect.iscoroutinefunction(adapter.fetch_races):
                result = await adapter.fetch_races(date, self.http_client)
            else:
                # This is a legacy, synchronous adapter. Run it in a separate thread.
                self.logger.warning(
                    "legacy_sync_adapter_detected",
                    adapter=adapter.source_name,
                    recommendation="This adapter should be refactored to be fully asynchronous."
                )
                result = await asyncio.to_thread(adapter.fetch_races, date, self.http_client)

            # Assuming the result is a dictionary with a 'races' key
            if result and 'races' in result:
                races = result.get('races', [])
                is_success = True
            else:
                error_message = "Adapter returned no data or malformed response"

        except Exception as e:
            self.logger.error(
                "Critical failure during fetch from adapter.",
                adapter=adapter.source_name,
                error=str(e),
                exc_info=True
            )
            error_message = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        health_monitor.record_adapter_response(adapter.source_name, success=is_success, duration=duration)

        # Construct a consistent source_info payload regardless of success or failure
        payload = {
            "races": races,
            "source_info": {
                "name": adapter.source_name,
                "status": "SUCCESS" if is_success else "FAILED",
                "races_fetched": len(races),
                "error_message": error_message,
                "fetch_duration": duration,
            },
        }
        return (adapter.source_name, payload, duration)

    def _race_key(self, race: Race) -> str:
        return f"{race.venue.lower().strip()}|{race.race_number}|{race.start_time.strftime('%H:%M')}"

    def _dedupe_races(self, races: List[Race]) -> List[Race]:
        """Deduplicates races from multiple sources and reconciles odds."""
        race_map: Dict[str, Race] = {}
        for race in races:
            # Use a robust key: venue, date, and race number
            key = f"{race.venue.upper()}-{race.start_time.strftime('%Y-%m-%d')}-{race.race_number}"

            if key not in race_map:
                race_map[key] = race
            else:
                # Merge runners and odds into the existing race object
                existing_race = race_map[key]
                runner_map = {r.number: r for r in existing_race.runners}

                for new_runner in race.runners:
                    if new_runner.number in runner_map:
                        # Runner exists, reconcile odds
                        existing_runner = runner_map[new_runner.number]
                        updated_odds = existing_runner.odds.copy()
                        updated_odds.update(new_runner.odds)
                        existing_runner.odds = updated_odds
                    else:
                        # New runner, add to the existing race
                        existing_race.runners.append(new_runner)

                # Update source count
                existing_race.source += f", {race.source}"

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
        match = re.search(r"\d+", v3_race.race_name)
        if match:
            race_number = int(match.group())

        runners = []
        for v3_runner in v3_race.runners:
            odds_data = OddsData(
                win=Decimal(str(v3_runner.odds_decimal)),
                source=v3_race.source_ids[0],
                last_updated=datetime.now(timezone.utc),
            )
            runner = Runner(
                id=v3_runner.runner_id,
                name=v3_runner.name,
                number=int(v3_runner.saddle_cloth)
                if v3_runner.saddle_cloth and v3_runner.saddle_cloth.isdigit()
                else 99,
                odds={v3_race.source_ids[0]: odds_data},
            )
            runners.append(runner)

        return Race(
            id=v3_race.race_key,
            venue=v3_race.track_key,
            race_number=race_number,
            start_time=datetime.fromisoformat(v3_race.start_time_iso),
            runners=runners,
            source=v3_race.source_ids[0],
            race_name=v3_race.race_name,
        )

    @cache_async_result(ttl_seconds=300, key_prefix="odds_engine_fetch")
    async def _fetch_races_from_sources(self, date: str, source_filter: str = None) -> Dict[str, Any]:
        """Helper method to contain the logic for fetching and aggregating races."""
        target_adapters = self.adapters
        if source_filter:
            target_adapters = [a for a in self.adapters if a.source_name.lower() == source_filter.lower()]

        tasks = [self._time_adapter_fetch(adapter, date) for adapter in target_adapters]

        # Run V3 adapters
        for adapter in self.v3_adapters:
            if hasattr(adapter, 'fetch_and_normalize'):
                # Handle synchronous V3 adapters
                v3_task = asyncio.to_thread(adapter.fetch_and_normalize)
                tasks.append(v3_task)
            elif hasattr(adapter, 'get_races'):
                # Handle asynchronous V3 adapters
                v3_task = adapter.get_races(date)
                tasks.append(v3_task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        source_infos = []
        all_races = []

        v3_start_time = datetime.now()  # Approximate start time for all V3 adapters

        for result in results:
            try:
                if isinstance(result, Exception):
                    self.log.error("Adapter fetch failed", error=result, exc_info=False)
                    continue

                # Correctly differentiate between V2 and V3 results
                if isinstance(result, tuple) and len(result) == 3:  # V2 Adapter Result
                    adapter_name, adapter_result, duration = result
                    source_info = adapter_result.get("source_info", {})
                    source_info["fetch_duration"] = round(duration, 2)
                    source_infos.append(source_info)
                    if source_info.get("status") == "SUCCESS":
                        all_races.extend(adapter_result.get("races", []))
                elif isinstance(result, list) and all(
                    isinstance(r, NormalizedRace) for r in result
                ):  # V3 Adapter Result
                    if result:
                        v3_races = result
                        adapter_name = v3_races[0].source_ids[0]
                        translated_races = [self._translate_v3_race_to_v2(nr) for nr in result]
                        all_races.extend(translated_races)

                        v3_duration = (datetime.now() - v3_start_time).total_seconds()
                        source_infos.append(
                            {
                                "name": adapter_name,
                                "status": "SUCCESS",
                                "races_fetched": len(translated_races),
                                "error_message": None,
                                "fetch_duration": round(v3_duration, 2),
                            }
                        )
            except Exception:
                self.log.error("Failed to process result from an adapter.", exc_info=True)

        deduped_races = self._dedupe_races(all_races)

        response_obj = AggregatedResponse(
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            races=deduped_races,
            sources=source_infos,
            metadata={
                "fetch_time": datetime.now(),
                "sources_queried": [a.source_name for a in target_adapters],
                "sources_successful": len([s for s in source_infos if s["status"] == "SUCCESS"]),
                "total_races": len(deduped_races),
            },
        )

        # --- Add Success Notification ---
        try:
            from windows_toasts import Toast, WindowsToaster
            toaster = WindowsToaster("Fortuna Faucet Data Refresh")
            new_toast = Toast()
            new_toast.text_fields = [f"Successfully fetched {len(deduped_races)} races from {len(source_infos)} sources."]
            toaster.show_toast(new_toast)
        except (ImportError, RuntimeError):
            pass

        return response_obj.model_dump()

    def _translate_v3_race_to_v2(self, norm_race: NormalizedRace) -> Race:
        """Translates a V3 NormalizedRace into a V2 Race object."""
        import re

        race_number = 0
        match = re.search(r"R(\d+)", norm_race.race_name)
        if match:
            race_number = int(match.group(1))

        runners = []
        for norm_runner in norm_race.runners:
            adapter_name = norm_race.source_ids[0] if norm_race.source_ids else "UnknownV3"
            odds_data = OddsData(
                win=Decimal(str(norm_runner.odds_decimal)), source=adapter_name, last_updated=datetime.now(timezone.utc)
            )

            try:
                runner_number = int(norm_runner.saddle_cloth)
            except (ValueError, TypeError):
                runner_number = None

            runner = Runner(
                id=norm_runner.runner_id, name=norm_runner.name, number=runner_number, odds={adapter_name: odds_data}
            )
            runners.append(runner)

        return Race(
            id=norm_race.race_key,
            venue=norm_race.track_key,
            start_time=datetime.fromisoformat(norm_race.start_time_iso),
            race_number=race_number,
            runners=runners,
            source=norm_race.source_ids[0] if norm_race.source_ids else "UnknownV3",
            # Store extra V3 data in metadata for future use
            metadata={"v3_race_name": norm_race.race_name},
        )
