import inspect
import logging
from typing import List

from . import adapters
from .scorer import RaceScorer
from .base import BaseAdapter, BaseAdapterV3
from .ui.terminal_ui import TerminalUI

def load_adapters(specific_source: str = None) -> List[type]:
    """
    Dynamically loads adapter classes from the adapters module.
    If a specific_source is provided, only that adapter is loaded.
    """
    adapter_classes = []
    for name, obj in inspect.getmembers(adapters, inspect.isclass):
        if issubclass(obj, (BaseAdapter, BaseAdapterV3)) and obj not in (BaseAdapter, BaseAdapterV3):
            if specific_source and hasattr(obj, 'SOURCE_ID') and obj.SOURCE_ID != specific_source:
                continue
            adapter_classes.append(obj)
    return adapter_classes


async def run_pipeline(min_runners: int, specific_source: str = None):
    """
    Orchestrates the end-to-end pipeline for fetching, parsing, and scoring races.
    """
    ui = TerminalUI()
    ui.setup_logging()

    logging.info("--- Paddock Parser NG Pipeline Start ---")

    all_races = []
    adapter_classes = load_adapters(specific_source)

    if not adapter_classes:
        logging.warning(f"No adapters found for source: '{specific_source}'" if specific_source else "No adapters found at all.")
        return

    ui.start_fetching_progress(len(adapter_classes))

    for adapter_class in adapter_classes:
        adapter = adapter_class()
        logging.info(f"Running adapter: {getattr(adapter, 'SOURCE_ID', 'Unknown')}...")

        try:
            normalized_races = []
            if isinstance(adapter, BaseAdapterV3):
                races = await adapter.fetch()
                normalized_races.extend(races)
            elif isinstance(adapter, BaseAdapter):
                raw_data = adapter.fetch_data()
                normalized_races = adapter.parse_data(raw_data)

            if normalized_races:
                logging.info(f"Parsed {len(normalized_races)} races from {getattr(adapter, 'SOURCE_ID', 'Unknown')}.")
                all_races.extend(normalized_races)
            else:
                logging.warning(f"No races parsed for {getattr(adapter, 'SOURCE_ID', 'Unknown')}.")

        except NotImplementedError:
            logging.warning(f"Adapter {getattr(adapter, 'SOURCE_ID', 'Unknown')} does not support live fetching and was skipped.")
        except Exception as e:
            logging.error(f"Adapter {getattr(adapter, 'SOURCE_ID', 'Unknown')} failed: {e}", exc_info=True)
        finally:
            ui.update_fetching_progress()

    ui.stop_fetching_progress()

    if not all_races:
        logging.info("No races were successfully parsed from any source.")
        logging.info("--- Pipeline End ---")
        return

    # Filter races based on field size
    if min_runners > 1:
        all_races = [r for r in all_races if r.number_of_runners and r.number_of_runners >= min_runners]

    # Score the races
    scorer = RaceScorer()
    for race in all_races:
        race.score = scorer.score(race)

    # Sort races by score (descending)
    all_races.sort(key=lambda r: r.score or 0, reverse=True)

    # Display the results using the new TerminalUI
    ui.display_races(all_races)

    logging.info("--- Pipeline End ---")
