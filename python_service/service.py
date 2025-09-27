# service.py
# The main entry point for the Checkmate Windows Service

import asyncio
import logging
from engine import DatabaseHandler, TrifectaAnalyzer, Settings, Race, Runner # Import all necessary components

class CheckmateBackgroundService:
    def __init__(self):
        self.db_path = r"C:\CheckmateV7\data\races.db" # This will be configurable
        self.db_handler = DatabaseHandler(self.db_path)
        self.analyzer = TrifectaAnalyzer()
        self.settings = Settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Checkmate Service Initialized with Hardened Protocols.")

    async def run_once(self):
        self.logger.info("Executing single data collection and analysis cycle...")
        # 1. Fetch data (Orchestrator will be added here later)
        # For now, we use mock data
        mock_races = [
            Race(race_id="mock_1", track_name="Aqueduct", race_number=1, runners=[Runner(name="Horse A", odds=2.5)], source="mock"),
            Race(race_id="mock_2", track_name="Santa Anita", race_number=3, runners=[Runner(name="Horse B", odds=5.0)], source="mock")
        ]

        # 2. Analyze races ('Engine Does the Thinking')
        analyzed_races = [self.analyzer.analyze_race(race, self.settings) for race in mock_races]

        # 3. Update database with pre-analyzed results
        self.db_handler.update_races(analyzed_races)

        self.logger.info("Data collection and analysis cycle complete.")

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    service = CheckmateBackgroundService()
    await service.run_once()

if __name__ == "__main__":
    asyncio.run(main())