import argparse
import asyncio
import json
import logging

from .services import DataSourceOrchestrator, get_db_session
from .logic import TrifectaAnalyzer
from .models import RaceDataSchema, HorseSchema

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_as_text(races: list) -> str:
    """Formats a list of qualified races into a human-readable string."""
    if not races:
        return "No qualified races found."

    output = ["--- Qualified Races ---"]
    for race in races:
        output.append(
            f"Track: {race['track']}, Race: {race['raceNumber']}, "
            f"Score: {race['checkmateScore']}"
        )
    return "\n".join(output)

async def main():
    """
    Main entry point for the Checkmate V7 CLI.
    Orchestrates the fetching, analysis, and printing of race data.
    """
    parser = argparse.ArgumentParser(description="Checkmate V7 - Horse Racing Analysis Tool")
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'text'],
        default='text',
        help='The output format (json or text).'
    )
    args = parser.parse_args()

    logging.info("Initializing services...")
    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        analyzer = TrifectaAnalyzer()

        logging.info("Fetching race data from all sources...")
        raw_races, _ = await orchestrator.get_races()
        logging.info(f"Found {len(raw_races)} total races to analyze.")

        qualified_races = []
        logging.info("Analyzing races and filtering for qualified opportunities...")
        for raw_race in raw_races:
            # Map the simple `Race` object to the rich `RaceDataSchema`
            horses_for_schema = [
                HorseSchema(
                    id=f"{raw_race.race_id}-{r.program_number}",
                    name=r.name,
                    number=r.program_number or 0,
                    jockey=r.jockey or "N/A",
                    trainer=r.trainer or "N/A",
                    odds=r.odds or 0.0,
                    morningLine=0.0,
                    speed=0,
                    class_rating=0,
                    form="",
                    lastRaced=""
                ) for r in raw_race.runners
            ]

            race_data = RaceDataSchema(
                id=raw_race.race_id,
                track=raw_race.track_name,
                raceNumber=raw_race.race_number or 0,
                postTime=raw_race.post_time.isoformat() if raw_race.post_time else "",
                horses=horses_for_schema,
                conditions=raw_race.race_type or "Unknown",
                distance="N/A",
                surface="N/A"
            )

            # Use the TrifectaAnalyzer to score and qualify each race
            analysis_result = analyzer.analyze_race(race_data)

            if analysis_result["qualified"]:
                # Add the analysis results to the schema object before appending
                race_data.checkmateScore = analysis_result["checkmateScore"]
                race_data.qualified = analysis_result["qualified"]
                race_data.trifectaFactors = analysis_result["trifectaFactors"]
                qualified_races.append(race_data.model_dump())

        logging.info(f"Found {len(qualified_races)} qualified races.")

        if args.output == 'json':
            print(json.dumps(qualified_races, indent=2))
        else:
            print(format_as_text(qualified_races))

    except Exception as e:
        logging.error(f"An error occurred during the analysis pipeline: {e}", exc_info=True)
    finally:
        if session:
            session.close()
        logging.info("Pipeline finished.")

if __name__ == "__main__":
    asyncio.run(main())
