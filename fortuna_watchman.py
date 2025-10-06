#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Watchman
# ==============================================================================
# This is the master orchestrator for the Fortuna Faucet project.
# It executes the full, end-to-end handicapping strategy autonomously.
# ==============================================================================

import asyncio
import httpx
import structlog
from datetime import datetime, timedelta
from typing import List

# It is assumed that this script is run from a shell where the venv is active
# and PYTHONPATH is set to include the project root.
from python_service.config import get_settings
from python_service.engine import OddsEngine
from python_service.analyzer import AnalyzerEngine
from python_service.models import Race
from live_monitor import LiveOddsMonitor

log = structlog.get_logger(__name__)

class Watchman:
    """Orchestrates the daily operation of the Fortuna Faucet."""

    def __init__(self):
        self.settings = get_settings()
        self.odds_engine = OddsEngine(config=self.settings)
        self.analyzer_engine = AnalyzerEngine()
        self.live_monitor = LiveOddsMonitor(config=self.settings)

    async def get_initial_targets(self) -> List[Race]:
        """Uses the OddsEngine (Pillar 1) to get the day's qualified races."""
        log.info("Watchman: Acquiring initial targets for the day...")
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            # Fetch all raw data
            aggregated_data = await self.odds_engine.fetch_all_odds(today_str)
            all_races = aggregated_data.get('races', [])
            if not all_races:
                log.warning("Watchman: No races returned from OddsEngine.")
                return []

            # Analyze the data to get qualified targets
            analyzer = self.analyzer_engine.get_analyzer('trifecta')
            qualified_races = analyzer.qualify_races(all_races)
            log.info("Watchman: Initial target acquisition complete", target_count=len(qualified_races))
            return qualified_races
        except Exception as e:
            log.error("Watchman: Failed to get initial targets", error=str(e), exc_info=True)
            return []

    async def run_tactical_monitoring(self, targets: List[Race]):
        """Uses the LiveOddsMonitor (Pillar 3) on each target as it approaches post time."""
        log.info("Watchman: Entering tactical monitoring loop.")
        async with httpx.AsyncClient() as client:
            while True:
                now = datetime.now()
                upcoming_targets = [r for r in targets if now < r.start_time < now + timedelta(minutes=5)]

                if upcoming_targets:
                    for race in upcoming_targets:
                        log.info("Watchman: Deploying Live Monitor for approaching race", race_id=race.id, venue=race.venue, qualification_score=race.qualification_score)
                        updated_race = await self.live_monitor.monitor_race(race, client)
                        # In a full implementation, this updated_race object would be passed to an execution engine.
                        log.info("Watchman: Live monitoring complete for race", race_id=updated_race.id, final_odds_source=list(updated_race.runners[0].odds.keys()))
                        # Remove from target list to prevent re-monitoring
                        targets = [t for t in targets if t.id != race.id]

                if not targets:
                    log.info("Watchman: All targets for the day have been monitored. Mission complete.")
                    break

                await asyncio.sleep(30) # Check for upcoming races every 30 seconds

    async def execute_daily_protocol(self):
        """The main, end-to-end orchestration method."""
        log.info("--- Fortuna Watchman Daily Protocol: ACTIVE ---")
        initial_targets = await self.get_initial_targets()
        if initial_targets:
            await self.run_tactical_monitoring(initial_targets)
        else:
            log.info("Watchman: No initial targets found. Shutting down for the day.")

        await self.odds_engine.close()
        log.info("--- Fortuna Watchman Daily Protocol: COMPLETE ---")

async def main():
    # Basic logging configuration for standalone script
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    watchman = Watchman()
    await watchman.execute_daily_protocol()

if __name__ == "__main__":
    asyncio.run(main())