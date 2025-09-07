import argparse
import logging
import asyncio

from .pipeline import run_pipeline
from .ui.terminal_ui import TerminalUI
from . import __version__
from . import config

def main():
    """
    The main entry point for the Paddock Parser application.
    """
    parser = argparse.ArgumentParser(
        description=f"Paddock Parser NG (Version {__version__}) - A toolkit for analyzing racecards."
    )

    parser.add_argument(
        '--source',
        type=str,
        help='Specify a single adapter to run (e.g., "skysports").'
    )

    parser.add_argument(
        '--min-runners',
        type=int,
        default=config.MIN_RUNNERS,
        help='The minimum number of runners for a race to be considered interesting.'
    )

    parser.add_argument(
        '--time-window',
        type=int,
        default=config.TIME_WINDOW_MINUTES,
        help='The time window in minutes from now to include races.'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging output.'
    )

    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # The pipeline now returns the data, so we need to handle the display here.
    ui = TerminalUI()
    ui.setup_logging() # The UI can still manage the logging format.

    races = asyncio.run(run_pipeline(
        min_runners=args.min_runners,
        time_window_minutes=args.time_window,
        specific_source=args.source,
        ui=ui # Pass the UI for progress updates
    ))

    if races:
        ui.display_races(races)

if __name__ == "__main__":
    main()
