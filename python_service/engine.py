# python_service/engine.py

import asyncio
import logging
import time
from typing import Dict, Any, List

# Assuming adapters are defined elsewhere and imported
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

class EngineManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters = [BetfairAdapter(), TVGAdapter(), RacingAndSportsAdapter(), PointsBetAdapter()]
        self.fetch_interval = 60 # seconds
        self.last_races: Dict[str, Any] = {}
        self._lock = asyncio.Lock() # CRITICAL FIX 3: Add lock for race condition protection

    async def fetch_all_races(self) -> None:
        """Fetches races from all adapters and updates the shared state under a lock."""
        self.logger.info("Starting parallel fetch from all adapters...")
        tasks = [adapter.fetch_races() for adapter in self.adapters]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # CRITICAL FIX 3: Protect the update of shared state
        async with self._lock:
            all_races: List[Dict] = []
            errors: List[Dict] = []

            for i, result in enumerate(results):
                adapter_name = self.adapters[i].__class__.__name__
                if isinstance(result, Exception):
                    errors.append({"adapter": adapter_name, "error": str(result)})
                    self.logger.error(f"Adapter {adapter_name} failed: {result}")
                elif result:
                    # Assuming a consistent return structure from adapters
                    all_races.extend(result.get("races", []))
                    if result.get("error"):
                        errors.append({"adapter": adapter_name, "error": result["error"]})

            self.last_races = {
                "races": all_races,
                "errors": errors,
                "timestamp": time.time()
            }
            self.logger.info(f"Fetch complete. Found {len(all_races)} races. Encountered {len(errors)} errors.")

    async def run(self):
        """The main background loop for the engine."""
        while True:
            try:
                await self.fetch_all_races()
                await asyncio.sleep(self.fetch_interval)
            except asyncio.CancelledError:
                self.logger.info("Engine run loop cancelled.")
                break
            except Exception as e:
                self.logger.error(f"An unexpected error occurred in the engine loop: {e}", exc_info=True)
                # Avoid rapid failure loops
                await asyncio.sleep(self.fetch_interval * 2)