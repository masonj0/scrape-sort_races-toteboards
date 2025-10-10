import anyio
import logging
from datetime import datetime
from typing import List, Dict

from .adapters.twinspires_adapter import TwinSpiresAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter
from .database.manager import DatabaseManager
from .models import NormalizedRace, Prediction

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_dynamic_odds_thresholds(field_size: int) -> Dict[str, float]:
    """Ported from the Checkmate Monitor JavaScript, this determines the odds
    thresholds for identifying an opportunity based on field size."""
    if field_size <= 4: return {"fav": 0.5, "secondFav": 2.0}
    if field_size == 5: return {"fav": 0.8, "secondFav": 3.0}
    if field_size == 6: return {"fav": 1.0, "secondFav": 3.5}
    return {"fav": 1.0, "secondFav": 4.0}

def find_checkmate_opportunities(races: List[NormalizedRace]) -> List[NormalizedRace]:
    """Ported from the Checkmate Monitor JavaScript, this filters a list of races
    to find 'Checkmate' opportunities based on the odds of the top two favorites."""
    opportunities = []
    for race in races:
        # The JS logic only applies to Thoroughbreds. The adapters should ideally provide this,
        # but for now, we assume they are returning relevant race types.
        if not race.runners or not (2 <= len(race.runners) < 7):
            continue

        # Ensure all runners have odds before sorting
        valid_runners = [r for r in race.runners if r.odds is not None]
        if len(valid_runners) < 2:
            continue

        sorted_runners = sorted(valid_runners, key=lambda r: r.odds)
        thresholds = get_dynamic_odds_thresholds(len(sorted_runners))

        fav = sorted_runners[0]
        second = sorted_runners[1]

        if fav.odds > thresholds["fav"] and second.odds > thresholds["secondFav"]:
            opportunities.append(race)
    return opportunities

class PredictionEngine:
    """
    The first engine in the "Closed Loop" architecture. It finds pre-race
    "Checkmate" opportunities and logs them to a permanent database.
    """
    def __init__(self, db_path: str = "paddock_parser.db"):
        self.db_manager = DatabaseManager(db_path)
        # Ensure tables exist before running
        self.db_manager.create_tables()
        self.adapters = {
            "TwinSpires": TwinSpiresAdapter(),
            "PointsBet": PointsBetAdapter()
            # RacingPost is an offline adapter and cannot be used in the live waterfall.
        }

    async def run_waterfall(self) -> List[NormalizedRace]:
        """
        Attempts to fetch race data from a series of adapters in a waterfall sequence.
        It stops and returns the data from the first successful adapter.
        """
        logging.info("Starting data acquisition waterfall...")
        # Order matches the "Gold -> Silver -> Contender" logic from the monitor
        waterfall_order = ["TwinSpires", "PointsBet"]

        for adapter_name in waterfall_order:
            adapter = self.adapters.get(adapter_name)
            if not adapter:
                continue

            logging.info(f"Attempting to fetch data from {adapter_name}...")
            try:
                races = await adapter.fetch()
                if races:
                    logging.info(f"Successfully fetched {len(races)} races from {adapter_name}.")
                    # Add source information to each race
                    for race in races:
                        race.source = adapter_name
                    return races
            except Exception as e:
                logging.error(f"Failed to fetch data from {adapter_name}: {e}", exc_info=True)

        logging.warning("Waterfall complete. No data was fetched from any source.")
        return []

    def process_and_log_opportunities(self, opportunities: List[NormalizedRace]):
        """
        Processes a list of opportunity races and saves them as Prediction records
        in the database.
        """
        if not opportunities:
            logging.info("No new checkmate opportunities found.")
            return

        logging.info(f"Found {len(opportunities)} new checkmate opportunities. Logging to database...")
        for opp in opportunities:
            sorted_runners = sorted([r for r in opp.runners if r.odds is not None], key=lambda r: r.odds)
            fav = sorted_runners[0]

            # Create a more robust race_id for the database
            race_id = f"{opp.source}-{opp.track}-{opp.race_time.strftime('%Y%m%d')}-R{opp.race_number}"

            prediction = Prediction(
                race_id=race_id,
                track=opp.track,
                race_number=opp.race_number,
                predicted_at=datetime.now(),
                favorite_name=fav.name,
                favorite_odds=fav.odds,
            )
            self.db_manager.save_prediction(prediction)

        logging.info(f"Successfully logged {len(opportunities)} predictions.")

    async def run(self):
        """Main execution method for the engine."""
        logging.info("Prediction Engine run started.")
        races = await self.run_waterfall()
        opportunities = find_checkmate_opportunities(races)
        self.process_and_log_opportunities(opportunities)
        self.db_manager.close()
        logging.info("Prediction Engine run finished.")

async def main():
    """Asynchronous entry point for the script."""
    engine = PredictionEngine()
    await engine.run()

if __name__ == "__main__":
    anyio.run(main)
