# src/paddock_parser/run.py

import argparse
import logging
import asyncio

# Correct, relative imports from within the package
from .pipeline import run_pipeline
from . import __version__

def main():
    """
    The main entry point for the Paddock Parser application.
    """
    # NOTE: The TerminalUI setup in the pipeline will take over logging.
    # This basicConfig is a fallback.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        default=8,
        help='The minimum number of runners for a race to be considered interesting.'
    )

    args = parser.parse_args()

    # Run the async pipeline using asyncio.run()
    asyncio.run(run_pipeline(
        min_runners=args.min_runners,
        specific_source=args.source
    ))

if __name__ == "__main__":
    main()
