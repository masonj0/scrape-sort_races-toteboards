import inspect
import logging
from typing import List, Optional

from . import adapters
from .scorer import RaceScorer
from .base import BaseAdapter, BaseAdapterV3, NormalizedRace
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
    """Converts a NormalizedRace from the base model to a Race from the app model."""
    return Race(
        race_id=norm_race.race_id,
        venue=norm_race.track_name,
        race_time=norm_race.post_time.strftime("%H:%M") if norm_race.post_time else "",
        race_number=norm_race.race_number,
        is_handicap=norm_race.race_type == "Handicap", # Assumption
        source=source,
        runners=[Runner(name=r.name, odds=str(r.odds) if r.odds else "SP") for r in norm_race.runners]
    )

def _convert_to_normalized_race(model_race: Race) -> NormalizedRace:
    """Converts a Race from the app model back to a NormalizedRace for pipeline output."""
    from datetime import datetime, date
    try:
        post_time = datetime.combine(date.today(), datetime.strptime(model_race.race_time, "%H:%M").time())
    except (ValueError, TypeError):
        post_time = None

    return NormalizedRace(
        race_id=model_race.race_id,
        track_name=model_race.venue,
        race_number=model_race.race_number,
        post_time=post_time,
        number_of_runners=len(model_race.runners),
        race_type="Handicap" if model_race.is_handicap else "Unknown",
        # The 'sources' field from the merged race is not stored in NormalizedRace
    )

async def run_pipeline(
    min_runners: int,
    specific_source: str = None,
    ui: Optional['TerminalUI'] = None
) -> List[NormalizedRace]:
    """Orchestrates the end-to-end pipeline."""
    logging.info("--- Paddock Parser NG Pipeline Start ---")

    unmerged_races = []
    adapter_classes = load_adapters(specific_source)

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
            normalized_races = []
            if isinstance(adapter, BaseAdapterV3):
                races = await adapter.fetch()
                normalized_races.extend(races)
            elif isinstance(adapter, BaseAdapter):
                raw_data = adapter.fetch_data()
                normalized_races = adapter.parse_data(raw_data)

            if normalized_races:
                logging.info(f"Parsed {len(normalized_races)} races from {source_id}.")
                # Convert to the application's Race model for merging
                for norm_race in normalized_races:
                    unmerged_races.append(_convert_to_model_race(norm_race, source_id))
            else:
                logging.warning(f"No races parsed for {source_id}.")

        except Exception as e:
            logging.error(f"Adapter {source_id} failed: {e}", exc_info=True)
        finally:
            if ui:
                ui.update_fetching_progress()

    if ui:
        ui.stop_fetching_progress()

    if not unmerged_races:
        logging.info("No races were successfully parsed from any source.")
        return []

    # Merge the races
    logging.info(f"Merging {len(unmerged_races)} race records...")
    merged_model_races = smart_merge(unmerged_races)
    logging.info(f"Merged down to {len(merged_model_races)} unique races.")

    # Convert back to NormalizedRace for scoring and final output
    final_normalized_races = [_convert_to_normalized_race(r) for r in merged_model_races]

    if min_runners > 1:
        final_normalized_races = [r for r in final_normalized_races if r.number_of_runners and r.number_of_runners >= min_runners]

    scorer = RaceScorer()
    for race in final_normalized_races:
        race.score = scorer.score(race)

    final_normalized_races.sort(key=lambda r: r.score or 0, reverse=True)

    logging.info("--- Pipeline End ---")
    return final_normalized_races
