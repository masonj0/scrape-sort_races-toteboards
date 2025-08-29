import inspect
import logging
from datetime import datetime

from . import adapters
from .analysis.scorer import RaceScorer
from .adapters.base import BaseAdapter, BaseAdapterV3
from .utils.browser import view_text_website  # This will be a mockable function for tests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_adapters():
    """
    Dynamically loads all adapter classes from the adapters module.
    """
    adapter_classes = []
    for name, obj in inspect.getmembers(adapters, inspect.isclass):
        if issubclass(obj, (BaseAdapter, BaseAdapterV3)) and obj not in (BaseAdapter, BaseAdapterV3):
            adapter_classes.append(obj)
    return adapter_classes


def run_analysis_pipeline(args):
    """
    Orchestrates the end-to-end pipeline for fetching, parsing, and scoring races.
    """
    logging.info("--- Paddock Parser NG Pipeline Start ---")

    all_races = []
    adapter_classes = load_adapters()
    logging.info(f"Found {len(adapter_classes)} adapters to run.")

    for adapter_class in adapter_classes:
        adapter = adapter_class()
        logging.info(f"\nRunning adapter: {adapter.SOURCE_ID}...")

        try:
            # For now, we assume V3 adapters have a URL and parse HTML
            if isinstance(adapter, BaseAdapterV3) and hasattr(adapter, 'url'):
                logging.info(f"Fetching data from {adapter.url}...")
                html_content = view_text_website(adapter.url)

                if html_content:
                    normalized_races = adapter.parse_races(html_content)
                    logging.info(f"Parsed {len(normalized_races)} races from {adapter.SOURCE_ID}.")
                    all_races.extend(normalized_races)
                else:
                    logging.warning(f"No content fetched for {adapter.SOURCE_ID}.")

            # Handle the placeholder FanDuel adapter gracefully
            elif adapter.SOURCE_ID == "fanduel":
                 logging.info("Skipping placeholder FanDuel adapter.")
                 continue

        except Exception as e:
            logging.error(f"Adapter {adapter.SOURCE_ID} failed: {e}", exc_info=True)
            continue

    if not all_races:
        logging.info("\nNo races were successfully parsed from any source.")
        logging.info("--- Pipeline End ---")
        return

    # Filter races based on field size
    if args.min_field_size > 1:
        all_races = [r for r in all_races if r.number_of_runners and r.number_of_runners >= args.min_field_size]
    if args.max_field_size:
        all_races = [r for r in all_races if r.number_of_runners and r.number_of_runners <= args.max_field_size]

    # Score the collected races
    if not args.no_odds_mode:
        logging.info(f"\nScoring {len(all_races)} races...")
        scorer = RaceScorer()
        scored_races = []
        for race in all_races:
            # Filter by min_score
            score = scorer.score(race)
            if score >= args.min_score:
                scored_races.append({"race": race, "score": score})
    else:
        logging.info("\n--no-odds-mode enabled, skipping scoring.")
        scored_races = [{"race": race, "score": 0} for race in all_races]

    # Sort the results based on the --sort-by argument
    logging.info(f"Sorting results by {args.sort_by}...")
    reverse_sort = True
    if args.sort_by == 'score':
        sort_key = lambda x: x['score']
    elif args.sort_by == 'field_size':
        sort_key = lambda x: x['race'].number_of_runners or 0
    elif args.sort_by == 'time':
        reverse_sort = False
        sort_key = lambda x: x['race'].post_time if x['race'].post_time else datetime.max
    else:
        logging.warning(f"Invalid sort key '{args.sort_by}'. Defaulting to sort by score.")
        sort_key = lambda x: x['score']

    sorted_races = sorted(scored_races, key=sort_key, reverse=reverse_sort)

    # Limit the results based on the --limit argument
    limited_races = sorted_races[:args.limit]

    # Display the top results
    logging.info(f"\n--- Top {args.limit} Scored Races ---")
    for i, result in enumerate(limited_races):
        race = result['race']
        score = result['score']
        logging.info(
            f"{i+1}. "
            f"Track: {race.track_name}, "
            f"Race: {race.race_number}, "
            f"Runners: {race.number_of_runners}, "
            f"Score: {score:.2f}"
        )

    logging.info("\n--- Pipeline End ---")
