"""
Checkmate V7: run.py - The "One-Shot" CLI Entrypoint
"""
import argparse
import json
import logging
from datetime import datetime
from typing import List, Dict

from .services import DataSourceOrchestrator, get_db_session
from .logic import TrifectaAnalyzer
from .models import Race, RaceDataSchema, HorseSchema
from tabulate import tabulate
from colorama import Fore, Style, init

def setup_logging():
    """Sets up basic logging for the CLI tool."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

def display_adapter_status(statuses: List[Dict]):
    """Displays the status of the data adapters in a colorized table."""
    headers = ["Adapter ID", "Status", "Races Found", "Notes"]
    table_data = []
    for status in statuses:
        status_color = Fore.GREEN if status['status'] == 'OK' else Fore.RED
        row = [
            status['adapter_id'],
            f"{status_color}{status['status']}{Style.RESET_ALL}",
            status['races_found'],
            status['notes']
        ]
        table_data.append(row)
    print("\n--- Adapter Status ---")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def display_race_summary(races: List[Race]):
    """Displays a summary of all fetched races."""
    headers = ["Track", "Race Number", "Post Time", "Runners"]
    table_data = [[r.track_name, r.race_number, r.post_time, r.number_of_runners] for r in races]
    print("\n--- All Races Fetched ---")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def display_qualified_races(tipsheet: List[Dict]):
    """Displays a detailed breakdown of Checkmate Qualified races."""
    if not tipsheet:
        print("\n--- No Checkmate Qualified Races Found ---")
        return

    headers = [
        "Track", "Race #", "Post Time",
        f"{Fore.CYAN}Score{Style.RESET_ALL}",
        f"{Fore.YELLOW}Trifecta Key{Style.RESET_ALL}",
        "Confidence", "Bet Type"
    ]
    table_data = []
    for tip in tipsheet:
        analysis = tip['analysis']
        row = [
            tip['trackName'],
            tip['raceNumber'],
            tip['postTime'],
            f"{Fore.CYAN}{analysis['checkmateScore']}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{analysis.get('trifectaKey', 'N/A')}{Style.RESET_ALL}",
            analysis.get('confidence', 'N/A'),
            analysis.get('betType', 'N/A')
        ]
        table_data.append(row)

    print("\n--- Checkmate Qualified Races ---")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def convert_race_to_schema(race: Race) -> RaceDataSchema:
    """
    Safely converts the internal Race dataclass to the RaceDataSchema Pydantic model.
    Provides default values for fields that may be missing from various adapters.
    """
    horses = []
    for r in race.runners:
        if r.odds is None:
            continue
        horses.append(HorseSchema(name=r.name, number=r.program_number, jockey=r.jockey, trainer=r.trainer, odds=r.odds))
    return RaceDataSchema(id=race.race_id, track=race.track_name, raceNumber=race.race_number, postTime=race.post_time.isoformat() if race.post_time else None, horses=horses)

def main():
    """
    Main execution function for the CLI.
    Fetches live race data, analyzes it, and generates a tipsheet.
    """
    init(autoreset=True)
    parser = argparse.ArgumentParser(description="Checkmate V7 - Jealousy Engine CLI")
    parser.add_argument("--output", choices=["json"], default="json", help="Specify the output format (only json is supported).")
    args = parser.parse_args()

    # setup_logging() # Disabled for cleaner table output
    print("--- Starting Checkmate V7 Showcase Run ---")

    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        analyzer = TrifectaAnalyzer()

        races, statuses = orchestrator.get_races()
        display_adapter_status(statuses)

        if not races:
            print("\nNo races were found by the orchestrator.")
        else:
            display_race_summary(races)
            tipsheet = []
            for race in races:
                race_schema = convert_race_to_schema(race)
                analysis = analyzer.analyze_race(race_schema)
                if analysis["qualified"]:
                    tipsheet.append({
                        "trackName": race.track_name,
                        "raceNumber": race.race_number,
                        "postTime": race.post_time.isoformat() if race.post_time else "N/A",
                        "checkmateScore": analysis["checkmateScore"],
                        "analysis": analysis,
                        "runners": [r.model_dump() for r in race_schema.horses]
                    })

            display_qualified_races(tipsheet)

            if args.output == "json":
                timestamp = datetime.now().strftime("%m%d_%Hh%M")
                output_filename = f"tipsheet_{timestamp}.json"
                print(f"\nWriting {len(tipsheet)} qualified races to {output_filename}...")
                with open(output_filename, "w") as f:
                    json.dump(tipsheet, f, indent=2)
                print("Successfully generated tipsheet.")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the run: {e}", exc_info=True)
    finally:
        if session:
            session.close()
        print("\n--- Checkmate V7 Showcase Run Finished ---")



if __name__ == "__main__":
    main()
