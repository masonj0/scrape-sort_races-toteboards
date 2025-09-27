# service.py
# The main entry point for the Checkmate Windows Service

import asyncio
import logging
from engine import DatabaseHandler # Placeholder for now

class CheckmateBackgroundService:
    def __init__(self):
        # This path will be configurable later
        self.db_path = r"C:\CheckmateV7\data\races.db"
        self.db_handler = DatabaseHandler(self.db_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Checkmate Service Initialized.")

    async def run_once(self):
        self.logger.info("Executing single data collection cycle...")
        # In the future, this will call the orchestrator and update the DB
        await asyncio.sleep(5) # Simulate work
        self.logger.info("Data collection cycle complete.")

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    service = CheckmateBackgroundService()
    await service.run_once()

if __name__ == "__main__":
    asyncio.run(main())