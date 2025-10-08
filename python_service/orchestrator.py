# python_service/orchestrator.py

import asyncio, structlog
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple, Type
import httpx

from .models import Race, RaceDay
from .adapter_anthology import (
    BaseAdapter,
    AtTheRacesAdapter,
    BetfairAdapter,
    BetfairGreyhoundAdapter,
    HarnessAdapter,
    RacingAndSportsAdapter,
    RacingAndSportsGreyhoundAdapter,
    SportingLifeAdapter,
    TimeformAdapter,
    TVGAdapter
)

log = structlog.get_logger(__name__)

ADAPTER_CLASSES: Tuple[Type[BaseAdapter], ...] = (
    AtTheRacesAdapter,
    BetfairAdapter,
    BetfairGreyhoundAdapter,
    HarnessAdapter,
    RacingAndSportsAdapter,
    RacingAndSportsGreyhoundAdapter,
    SportingLifeAdapter,
    TimeformAdapter,
    TVGAdapter
)

async def fetch_all_races(dedupe: bool = True) -> List[RaceDay]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        tasks = [_fetch_adapter(cls(client)) for cls in ADAPTER_CLASSES]
        results = await asyncio.gather(*tasks)
    all_races: List[Race] = [race for races in results for race in races]
    if dedupe: all_races = _dedupe_races(all_races)
    return _group_races_by_track(all_races)

def get_adapter_statuses() -> List[Dict[str, str]]:
    return [{"adapter_name": cls.SOURCE_NAME, "status": "OK"} for cls in ADAPTER_CLASSES]

async def _fetch_adapter(adapter: BaseAdapter) -> List[Race]:
    try:
        races = await adapter.get_races()
        log.info("Adapter fetched races", adapter=adapter.SOURCE_NAME, count=len(races))
        return races
    except Exception as exc:
        log.error("Adapter failed", adapter=adapter.SOURCE_NAME, error=exc, exc_info=True)
    return []

def _race_key(race: Race) -> str:
    return f"{race.venue.lower().strip()}|{race.race_number}|{race.start_time.strftime('%H:%M')}"

def _dedupe_races(races: Iterable[Race]) -> List[Race]:
    race_map: Dict[str, Race] = {}
    for race in sorted(races, key=lambda r: r.source, reverse=True): # Prioritize certain sources if needed
        key = _race_key(race)
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

def _group_races_by_track(races: Iterable[Race]) -> List[RaceDay]:
    track_map: Dict[str, List[Race]] = defaultdict(list)
    for race in races:
        if race and race.venue:
            track_map[race.venue].append(race)
    race_days = [RaceDay(track_name=name, races=sorted(r_list, key=lambda r: r.race_number)) for name, r_list in track_map.items()]
    return sorted(race_days, key=lambda rd: rd.track_name)