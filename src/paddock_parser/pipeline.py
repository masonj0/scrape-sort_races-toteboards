import inspect
import logging
from typing import List, Optional, Dict, Tuple

from . import adapters
from .scorer import RaceScorer
from .base import BaseAdapter, BaseAdapterV3, NormalizedRace, NormalizedRunner
from .merger import smart_merge
from .models import Race, Runner

# The TerminalUI class is forward-declared using a string to avoid circular import.
if False:
    from .ui.terminal_ui import TerminalUI

def load_adapters(specific_source: str = None) -> List[type]:
    """Dynamically loads adapter classes from the adapters module."""
    adapter_classes = []
    for name, obj in inspect.getmembers(adapters, inspect.isclass):
        if issubclass(obj, (BaseAdapter, BaseAdapterV3)) and obj not in (BaseAdapter, BaseAdapterV3):
            if specific_source and hasattr(obj, 'SOURCE_ID') and obj.SOURCE_ID != specific_source:
                continue
            adapter_classes.append(obj)
    return adapter_classes

def _convert_to_model_race(norm_race: NormalizedRace, source: str) -> Race:
    """
    Converts a NormalizedRace from the base model to a Race from the app model.
    NOTE: This conversion is lossy for program_number, which is handled by a
    workaround in the main pipeline logic.
    """
    is_handicap = norm_race.race_type and "handicap" in norm_race.race_type.lower()
    return Race(
        race_id=norm_race.race_id,
        venue=norm_race.track_name,
        race_time=norm_race.post_time.strftime("%H:%M") if norm_race.post_time else "",
        race_number=norm_race.race_number,
        number_of_runners=norm_race.number_of_runners,
        is_handicap=is_handicap,
        source=source,
        runners=[Runner(name=r.name, odds=r.odds) for r in norm_race.runners]
    )

def _convert_to_normalized_race(model_race: Race, prog_num_map: Dict[Tuple[str, str], int]) -> NormalizedRace:
    """Converts a Race from the app model back to a NormalizedRace for pipeline output."""
    from datetime import datetime, date
    try:
        post_time = datetime.combine(date.today(), datetime.strptime(model_race.race_time, "%H:%M").time())
    except (ValueError, TypeError):
        post_time = None

    # Reconstruct NormalizedRunner with program_number from the map
    runners = [
        NormalizedRunner(
            name=r.name,
            odds=r.odds,
            program_number=prog_num_map.get((model_race.race_id, r.name), i + 1) # Fallback to index
        ) for i, r in enumerate(model_race.runners)
    ]

    # Fix for the number_of_runners data loss bug (handles case where value is 0)
    num_runners = model_race.number_of_runners if model_race.number_of_runners is not None else len(runners)
    race_type = "Handicap" if model_race.is_handicap else "Unknown"

    return NormalizedRace(
        race_id=model_race.race_id,
        track_name=model_race.venue,
        race_number=model_race.race_number,
        post_time=post_time,
        number_of_runners=num_runners,
        race_type=race_type,
        runners=runners,
    )

async def run_pipeline(
    min_runners: int,
    time_window_minutes: int,
    specific_source: str = None,
    ui: Optional['TerminalUI'] = None
) -> List[NormalizedRace]:
    """Orchestrates the end-to-end pipeline."""
    logging.info("--- Paddock Parser NG Pipeline Start ---")

    unmerged_races: List[Race] = []
    prog_num_map: Dict[Tuple[str, str], int] = {}  # Map to preserve program numbers across lossy conversion
    adapter_classes = load_adapters(specific_source)
    races_per_adapter: Dict[str, int] = {}

    if not adapter_classes:
        logging.warning("No adapters found.")
        return []

    if ui:
        ui.start_fetching_progress(len(adapter_classes))

    for adapter_class in adapter_classes:
        adapter = adapter_class()
        source_id = getattr(adapter, 'SOURCE_ID', 'Unknown')
        logging.info(f"Running adapter: {source_id}...")

        try:
            normalized_races: List[NormalizedRace] = []
            if isinstance(adapter, BaseAdapterV3):
                races = await adapter.fetch()
                normalized_races.extend(races)
            elif isinstance(adapter, BaseAdapter):
                raw_data = adapter.fetch_data()
                normalized_races = adapter.parse_data(raw_data)

            races_per_adapter[source_id] = len(normalized_races)

            if normalized_races:
                logging.info(f"Parsed {len(normalized_races)} races from {source_id}.")
                # Convert to the application's Race model for merging
                for norm_race in normalized_races:
                    # Stash program numbers before they are lost in conversion
                    for runner in norm_race.runners:
                        if runner.program_number:
                            prog_num_map[(norm_race.race_id, runner.name)] = runner.program_number
                    unmerged_races.append(_convert_to_model_race(norm_race, source_id))
            else:
                logging.warning(f"No races parsed for {source_id}.")

        except NotImplementedError:
            logging.info(f"Adapter {source_id} skipped: Not implemented for live fetching.")
        except Exception:
            logging.error(f"An error occurred in the '{source_id}' adapter. See details below.", exc_info=True)
        finally:
            if ui:
                ui.update_fetching_progress()

    if ui:
        ui.stop_fetching_progress()

    logging.info("\n--- Data Ingestion Summary ---")
    for source, count in races_per_adapter.items():
        logging.info(f"  - {source}: {count} races")
    logging.info(f"Total races ingested: {len(unmerged_races)}")

    races_with_few_runners = [r for r in unmerged_races if r.number_of_runners and r.number_of_runners < 7]
    logging.info(f"Found {len(races_with_few_runners)} races with fewer than 7 runners.")
    logging.info("----------------------------\n")

    if not unmerged_races:
        logging.info("No races were successfully parsed from any source.")
        return []

    # Merge the races
    logging.info(f"Merging {len(unmerged_races)} race records...")
    merged_model_races = smart_merge(unmerged_races)
    logging.info(f"Merged down to {len(merged_model_races)} unique races.")

    # Score the merged races (which are Race models)
    scorer = RaceScorer()
    for race in merged_model_races:
        scores = scorer.score(race)
        setattr(race, 'scores', scores)
        setattr(race, 'score', scores.get('total_score', 0.0))

    # Filter based on min_runners
    if min_runners > 1:
        merged_model_races = [r for r in merged_model_races if r.number_of_runners >= min_runners]

    # Convert back to NormalizedRace for final output, preserving the score
    final_normalized_races = []
    for race_model in merged_model_races:
        norm_race = _convert_to_normalized_race(race_model, prog_num_map)
        norm_race.score = getattr(race_model, 'score', 0.0)
        norm_race.scores = getattr(race_model, 'scores', {})
        final_normalized_races.append(norm_race)

    # Filter by time window
    if time_window_minutes > 0:
        from datetime import datetime, timedelta
        now = datetime.now()
        time_limit = now + timedelta(minutes=time_window_minutes)
        races_before_time_filter = len(final_normalized_races)
        final_normalized_races = [
            r for r in final_normalized_races if r.post_time and r.post_time > now and r.post_time <= time_limit
        ]
        races_after_time_filter = len(final_normalized_races)
        logging.info(f"Filtered {races_before_time_filter} races down to {races_after_time_filter} races in the next {time_window_minutes} minutes.")

    # Sort the final list by score
    final_normalized_races.sort(key=lambda r: r.score or 0, reverse=True)

    logging.info("--- Pipeline End ---")
    return final_normalized_races
