import argparse
import logging
import asyncio

from .pipeline import run_pipeline
from .ui.terminal_ui import TerminalUI
from . import version
from . import config

def main():
    """
    The main entry point for the Paddock Parser application.
    """
    parser = argparse.ArgumentParser(
        description=f"Paddock Parser NG (Version {version}) - A toolkit for analyzing racecards."
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

    ui = TerminalUI()
    ui.setup_logging()

    races, enabled_adapter_count, successful_adapter_count = asyncio.run(run_pipeline(
        min_runners=args.min_runners,
        time_window_minutes=args.time_window,
        specific_source=args.source,
        ui=ui
    ))

    if races:
        ui.display_races(races)
    else:
        ui.console.print(
            f"[yellow]No races found from {enabled_adapter_count} enabled adapters "
            f"({successful_adapter_count} successfully returned data).[/yellow]"
        )

if __name__ == "__main__":
    main()
