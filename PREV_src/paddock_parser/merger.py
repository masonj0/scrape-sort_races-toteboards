from typing import List
from collections import defaultdict
from .models import Race

# Define the priority of the sources. Lower index = higher priority.
SOURCE_PRIORITY = ["FanDuel", "SkySports", "AtTheRaces"]

def get_source_priority(source: str) -> int:
    """Returns the priority of a source, with lower numbers being better."""
    try:
        return SOURCE_PRIORITY.index(source)
    except ValueError:
        return len(SOURCE_PRIORITY) # Lowest priority if not in the list

def smart_merge(races: List[Race]) -> List[Race]:
    """
    Deduplicates and merges a list of Race objects based on race_id.

    - Merges runner data, prioritizing odds from higher-priority sources.
    - Merges top-level metadata, taking it from the highest-priority source.
    - Tracks the provenance of the merged data in the 'sources' field.
    """
    # 1. Group races by race_id
    grouped_races = defaultdict(list)
    for race in races:
        grouped_races[race.race_id].append(race)

    merged_races = []
    for race_id, race_group in grouped_races.items():
        # 2. If only one race in the group, it's unique.
        if len(race_group) == 1:
            unique_race = race_group[0]
            # Initialize its provenance list
            unique_race.sources = [unique_race.source]
            merged_races.append(unique_race)
            continue

        # 3. If multiple races, merge them.
        # Sort the group by source priority to find the primary record.
        race_group.sort(key=lambda r: get_source_priority(r.source))

        primary_race = race_group[0]

        import logging
        # Create the new merged race object from the primary race's metadata.
        logging.info(f"Primary race number for {race_id}: {primary_race.race_number}")
        merged_race = Race(
            race_id=primary_race.race_id,
            venue=primary_race.venue,
            race_time=primary_race.race_time,
            race_number=primary_race.race_number,
            is_handicap=primary_race.is_handicap,
            source=primary_race.source # The source of the primary record
        )

        # 4. Track provenance
        merged_race.sources = sorted([r.source for r in race_group], key=get_source_priority)

        # 5. Merge runners, respecting priority
        merged_runners = {}
        # Iterate in reverse priority order (worst to best) so that higher priority
        # sources overwrite lower priority ones.
        for race in sorted(race_group, key=lambda r: get_source_priority(r.source), reverse=True):
            for runner in race.runners:
                merged_runners[runner.name] = runner

        merged_race.runners = list(merged_runners.values())

        merged_races.append(merged_race)

    return merged_races
