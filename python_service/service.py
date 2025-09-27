# service.py
# Fully activated to use the live data fleet.

import asyncio
import logging
from engine import DatabaseHandler, TrifectaAnalyzer, Settings, DataSourceOrchestrator

class CheckmateBackgroundService:
    def __init__(self):
        self.db_path = r"C:\CheckmateV7\data\races.db" # This will be configurable
        self.db_handler = DatabaseHandler(self.db_path)
        self.orchestrator = DataSourceOrchestrator()
        self.analyzer = TrifectaAnalyzer()
        self.settings = Settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Checkmate Service Initialized with Full Data Fleet.")

    async def run_once(self):
        self.logger.info("Executing live data collection and analysis cycle...")
        # 1. Fetch live data from all adapters concurrently
        live_races = self.orchestrator.get_races()

        # 2. Analyze all fetched races ('Engine Does the Thinking')
        analyzed_races = [self.analyzer.analyze_race(race, self.settings) for race in live_races]

        # 3. Update database with pre-analyzed results
        self.db_handler.update_races(analyzed_races)

        self.logger.info("Live data cycle complete.")

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    service = CheckmateBackgroundService()
    await service.run_once()

if __name__ == "__main__":
    asyncio.run(main())