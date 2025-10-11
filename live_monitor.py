#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Live Odds Monitor (The Third Pillar)
# ==============================================================================

import httpx
import structlog
from datetime import datetime

from python_service.models import Race, OddsData
from python_service.adapters.betfair_adapter import BetfairAdapter

log = structlog.get_logger(__name__)

from typing import Dict

class LiveOddsMonitor:
    """Monitors live odds for given race markets and triggers bets."""

    def __init__(self, betfair_adapter: BetfairAdapter):
        self.betfair_adapter = betfair_adapter
        self.monitored_markets: Dict[str, Race] = {}

    async def __aenter__(self):
        """Allows the monitor to be used as an async context manager."""
        log.info("LiveOddsMonitor entered context.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures resources are cleaned up when the context is exited."""
        log.info("LiveOddsMonitor exiting context, closing adapter resources...")
        await self.betfair_adapter.close()
        log.info("Adapter resources closed.")

    async def monitor_race(self, race: Race, http_client: httpx.AsyncClient) -> Race:
        """
        Monitors a single race, fetching live odds and updating the Race object.
        """
        log.info("Monitoring race for live odds", race_id=race.id, venue=race.venue)
        if not race.id.startswith('bf_'):
            log.warning("Cannot monitor non-Betfair race", race_id=race.id, source=race.source)
            return race # Return original race if not a Betfair market

        market_id = race.id.split('bf_')[1]

        try:
            live_odds = await self.betfair_adapter.get_live_odds_for_market(market_id, http_client)
            if not live_odds:
                log.warning("No live odds returned from Betfair", market_id=market_id)
                return race

            log.info("Successfully fetched live odds", market_id=market_id, odds_count=len(live_odds))
            # Update the runners in the Race object with the new live odds
            for runner in race.runners:
                if runner.selection_id in live_odds:
                    runner.odds[self.adapter.source_name] = OddsData(
                        win=live_odds[runner.selection_id],
                        source=self.adapter.source_name,
                        last_updated=datetime.now()
                    )
            return race
        except Exception as e:
            log.error("Failed to monitor race", race_id=race.id, error=e, exc_info=True)
            return race # Return original race on failure