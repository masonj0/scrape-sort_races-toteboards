"""
Checkmate V7: `run.py` - The "One-Shot" CLI Entrypoint
"""
import argparse
import json
import logging
from datetime import datetime

from .services import DataSourceOrchestrator, get_db_session
from .logic import TrifectaAnalyzer
from .models import Race, RaceDataSchema, HorseSchema

def setup_logging():
    """Sets up basic logging for the CLI tool."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )

def convert_race_to_schema(race: Race) -> RaceDataSchema:
    """
    Safely converts the internal Race dataclass to the RaceDataSchema Pydantic model.
    Provides default values for fields that may be missing from various adapters.
    """
    horses = []
    for r in race.runners:
        # The analyzer requires odds, so skip runners without them.
        if r.odds is None:
            continue

        horses.append(
            HorseSchema(
                name=r.name,
                number=r.program_number,
                jockey=r.jockey,
                trainer=r.trainer,
                odds=r.odds
                # Other fields like id, morningLine, etc., will use Pydantic's default None
            )
        )

    return RaceDataSchema(
        id=race.race_id,
        track=race.track_name,
        raceNumber=race.race_number,
        postTime=race.post_time.isoformat() if race.post_time else None,
        horses=horses
    )


def main():
    """
    Main execution function for the CLI.
    Fetches live race data, analyzes it, and generates a tipsheet.
    """
    parser = argparse.ArgumentParser(description="Checkmate V7 - Jealousy Engine CLI")
    parser.add_argument(
        "--output",
        choices=["json"],
        default="json",
        help="Specify the output format (only json is supported).",
    )
    args = parser.parse_args()

    setup_logging()
    logging.info("--- Starting Checkmate V7 Showcase Run ---")

    session = None
    try:
        logging.info("Initializing database session and orchestrator...")
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        analyzer = TrifectaAnalyzer()

        logging.info("Fetching live race data...")
        races, statuses = orchestrator.get_races()
        logging.info(f"Orchestrator status: {statuses}")

        tipsheet = []
        if not races:
            logging.warning("No races were found by the orchestrator.")
        else:
            logging.info(f"Found {len(races)} races. Analyzing for Checkmate opportunities...")
            for race in races:
                race_schema = convert_race_to_schema(race)
                analysis = analyzer.analyze_race(race_schema)

                if analysis["qualified"]:
                    logging.info(f"Checkmate QUALIFIED: {race.track_name} - Race {race.race_number} (Score: {analysis['checkmateScore']})")
                    tipsheet.append({
                        "trackName": race.track_name,
                        "raceNumber": race.race_number,
                        "postTime": race.post_time.isoformat() if race.post_time else None,
                        "checkmateScore": analysis["checkmateScore"],
                        "analysis": analysis,
                        "runners": [r.model_dump() for r in race_schema.horses]
                    })
                else:
                    logging.info(f"Checkmate SKIPPED: {race.track_name} - Race {race.race_number} (Score: {analysis['checkmateScore']})")

        if args.output == "json":
            output_filename = "tipsheet.json"
            logging.info(f"Writing {len(tipsheet)} qualified races to {output_filename}...")
            with open(output_filename, "w") as f:
                json.dump(tipsheet, f, indent=2)
            logging.info("Successfully generated tipsheet.")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the run: {e}", exc_info=True)
    finally:
        if session:
            session.close()
        logging.info("--- Checkmate V7 Showcase Run Finished ---")


if __name__ == "__main__":
    main()
