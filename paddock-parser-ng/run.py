import argparse
import asyncio
from paddock_parser.pipeline import run_analysis_pipeline

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Paddock Parser NG - Horse Racing Analysis Tool")

    # Core Configuration
    parser.add_argument('--config', type=str, help='Path to a configuration file.')
    parser.add_argument('--output', type=str, help='Path to output the report file.')

    # Scoring & Filtering
    parser.add_argument('--min-score', type=float, default=0.0, help='Minimum score to include in the report.')
    parser.add_argument('--no-odds-mode', action='store_true', help='Run in "no odds" mode, skipping the scoring step.')

    # Field Size Filtering
    parser.add_argument('--min-field-size', type=int, default=1, help='Minimum number of runners in a race.')
    parser.add_argument('--max-field-size', type=int, help='Maximum number of runners in a race.')

    # Output Control
    parser.add_argument('--sort-by', type=str, default='score', choices=['score', 'field_size', 'time'], help='Field to sort the final report by.')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to display in the report.')

    return parser.parse_args()

def main():
    """
    Main entry point for the Paddock Parser NG application.
    """
    args = parse_arguments()
    run_analysis_pipeline(args)

if __name__ == "__main__":
    main()
