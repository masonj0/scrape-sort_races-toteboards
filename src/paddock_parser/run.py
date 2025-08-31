# src/paddock_parser/run.py

import argparse
import logging

# Correct, relative imports from within the package
from .pipeline import run_pipeline
from . import __version__ # Example of another top-level import

def main():
    """
    The main entry point for the Paddock Parser application.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(
        description=f"Paddock Parser NG (Version {__version__}) - A toolkit for analyzing racecards."
    )

    parser.add_argument(
        '--source',
        type=str,
        help='Specify a single adapter to run (e.g., "equibase").'
    )

    parser.add_argument(
        '--min-runners',
        type=int,
        default=8,
        help='The minimum number of runners for a race to be considered interesting.'
    )

    args = parser.parse_args()

    logging.info("Starting Paddock Parser NG...")

    # Note the correct way to call the pipeline function
    run_pipeline(
        min_runners=args.min_runners,
        specific_source=args.source
    )

    logging.info("Paddock Parser NG finished.")

if __name__ == "__main__":
    main()
