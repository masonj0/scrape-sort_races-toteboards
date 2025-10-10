#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Watchman (v2 - Score-Aware)
# ==============================================================================
# This is the master orchestrator for the Fortuna Faucet project.
# It executes the full, end-to-end handicapping strategy autonomously.
# ==============================================================================

import asyncio
import httpx
import structlog
from datetime import datetime, timedelta, timezone
from typing import List

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
        """Uses the OddsEngine and AnalyzerEngine to get the day's ranked targets."""
        log.info("Watchman: Acquiring and ranking initial targets for the day...")
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        try:
            aggregated_data = await self.odds_engine.fetch_all_odds(today_str)
            all_races = aggregated_data.get('races', [])
            if not all_races:
                log.warning("Watchman: No races returned from OddsEngine.")
                return []

            analyzer = self.analyzer_engine.get_analyzer('trifecta')
            qualified_races = analyzer.qualify_races(all_races) # This now returns a sorted list with scores
            log.info("Watchman: Initial target acquisition and ranking complete", target_count=len(qualified_races))

            # Log the top targets for better observability
            for race in qualified_races[:5]:
                log.info("Top Target Found",
                    score=race.qualification_score,
                    venue=race.venue,
                    race_number=race.race_number,
                    post_time=race.start_time.isoformat()
                )
            return qualified_races
        except Exception as e:
            log.error("Watchman: Failed to get initial targets", error=str(e), exc_info=True)
            return []

    async def run_tactical_monitoring(self, targets: List[Race]):
        """Uses the LiveOddsMonitor on each target as it approaches post time."""
        log.info("Watchman: Entering tactical monitoring loop.")
        active_targets = list(targets)
        async with httpx.AsyncClient() as client:
            while active_targets:
                now = datetime.now(timezone.utc)

                # Find races that are within the 5-minute monitoring window
                races_to_monitor = [r for r in active_targets if r.start_time.replace(tzinfo=timezone.utc) > now and r.start_time.replace(tzinfo=timezone.utc) < now + timedelta(minutes=5)]

                if races_to_monitor:
                    for race in races_to_monitor:
                        log.info("Watchman: Deploying Live Monitor for approaching target",
                            race_id=race.id,
                            venue=race.venue,
                            score=race.qualification_score
                        )
                        updated_race = await self.live_monitor.monitor_race(race, client)
                        log.info("Watchman: Live monitoring complete for race", race_id=updated_race.id)
                        # Remove from target list to prevent re-monitoring
                        active_targets = [t for t in active_targets if t.id != race.id]

                if not active_targets:
                    break # Exit loop if all targets are processed

                await asyncio.sleep(30) # Check for upcoming races every 30 seconds

        log.info("Watchman: All targets for the day have been monitored. Mission complete.")

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
    from python_service.logging_config import configure_logging
    configure_logging()
    watchman = Watchman()
    await watchman.execute_daily_protocol()

if __name__ == "__main__":
    asyncio.run(main())