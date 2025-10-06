#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Live Odds Monitor (The Third Pillar)
# ==============================================================================

import asyncio
import httpx
import structlog
from datetime import datetime
from typing import List
from python_service.models import Race
from python_service.adapters.oddschecker_adapter import OddscheckerAdapter

log = structlog.get_logger(__name__)

class LiveOddsMonitor:
    """
    The 'Third Pillar' of the architecture.
    This engine uses fast, live-odds adapters to get a final snapshot of the
    market in the crucial moments before a race.
    """

    def __init__(self, config):
        self.config = config
        log.info("LiveOddsMonitor initialized. (Functional with Oddschecker)")

    async def get_live_snapshot(self, http_client: httpx.AsyncClient) -> List[Race]:
        """
        Uses a fast, live-odds adapter to get a full snapshot of today's races.

        Returns:
            A list of Race objects with the most up-to-date odds available.
        """
        log.info("LiveOddsMonitor: Fetching live snapshot from Oddschecker...")
        try:
            adapter = OddscheckerAdapter(config=self.config)
            # The date param is not strictly used by this adapter but is required by the interface
            today_str = datetime.now().strftime('%Y-%m-%d')
            result = await adapter.fetch_races(today_str, http_client)

            # The adapter now returns a dict, we need to deserialize the races
            races = [Race.model_validate(r) for r in result.get('races', [])]
            log.info("LiveOddsMonitor: Snapshot successful", races_found=len(races))
            return races
        except Exception as e:
            log.error("LiveOddsMonitor: Failed to get live snapshot", error=e, exc_info=True)
            return []

# Example of how this might be orchestrated in the future
async def example_run(config):
    log.info("--- Live Monitor Example Run --- ")
    monitor = LiveOddsMonitor(config)
    async with httpx.AsyncClient() as client:
        live_races = await monitor.get_live_snapshot(client)
        if live_races:
            # A future analyzer could now compare these live odds against the
            # earlier, qualified races from the main OddsEngine.
            log.info("Example: First live race found", venue=live_races[0].venue, race=live_races[0].race_number)