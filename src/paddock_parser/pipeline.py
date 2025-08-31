import inspect
import logging
import asyncio
from datetime import datetime

from . import adapters
from .scorer import RaceScorer
from .base import BaseAdapter, BaseAdapterV3

def load_adapters(specific_source: str = None):
    """
    Dynamically loads adapter classes from the adapters module.
    If a specific_source is provided, only that adapter is loaded.
    """
    adapter_classes = []
    for name, obj in inspect.getmembers(adapters, inspect.isclass):
        if issubclass(obj, (BaseAdapter, BaseAdapterV3)) and obj not in (BaseAdapter, BaseAdapterV3):
            if specific_source and obj.SOURCE_ID != specific_source:
                continue
            adapter_classes.append(obj)
    return adapter_classes


async def run_pipeline(min_runners: int, specific_source: str = None):
    """
    Orchestrates the end-to-end pipeline for fetching, parsing, and scoring races.
    """
    logging.info("--- Paddock Parser NG Pipeline Start ---")

    all_races = []
    adapter_classes = load_adapters(specific_source)

    if not adapter_classes:
        logging.warning(f"No adapters found for source: {specific_source}" if specific_source else "No adapters found at all.")
        return

    logging.info(f"Found {len(adapter_classes)} adapters to run.")

    for adapter_class in adapter_classes:
        adapter = adapter_class()
        logging.info(f"\nRunning adapter: {adapter.SOURCE_ID}...")

        try:
            normalized_races = []
            if isinstance(adapter, BaseAdapterV3):
                races = await adapter.fetch()
                normalized_races.extend(races)
            elif isinstance(adapter, BaseAdapter):
                raw_data = adapter.fetch_data()
                normalized_races = adapter.parse_data(raw_data)

            if normalized_races:
                logging.info(f"Parsed {len(normalized_races)} races from {adapter.SOURCE_ID}.")
                all_races.extend(normalized_races)
            else:
                logging.warning(f"No races parsed for {adapter.SOURCE_ID}.")

        except NotImplementedError:
            logging.warning(f"Adapter {adapter.SOURCE_ID} does not support live fetching and was skipped.")
            continue
        except Exception as e:
            logging.error(f"Adapter {adapter.SOURCE_ID} failed: {e}", exc_info=True)
            continue

    if not all_races:
        logging.info("\nNo races were successfully parsed from any source.")
        logging.info("--- Pipeline End ---")
        return

    # Filter races based on field size
    if min_runners > 1:
        all_races = [r for r in all_races if r.number_of_runners and r.number_of_runners >= min_runners]

    # For now, we will just print the races, as scoring and sorting are not part of the new design.
    # This can be added back later.
    logging.info(f"\n--- Found {len(all_races)} Races Matching Criteria ---")
    for i, race in enumerate(all_races):
        logging.info(
            f"{i+1}. "
            f"Track: {race.track_name}, "
            f"Race: {race.race_number}, "
            f"Runners: {race.number_of_runners}"
        )

    logging.info("\n--- Pipeline End ---")
