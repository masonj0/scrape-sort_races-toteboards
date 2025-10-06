#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Betfair API Adapter (Canonized)
# ==============================================================================
# This adapter is a production-grade API client for the Betfair Exchange.
# It is the primary weapon for the LiveOddsMonitor (The Third Pillar).
# ==============================================================================

import httpx
import structlog
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

log = structlog.get_logger(__name__)

class BetfairAdapter(BaseAdapter):
    """API client for the Betfair Exchange, focused on live odds."""

    def __init__(self, config):
        super().__init__(source_name="BetfairExchange", base_url="https://api.betfair.com/exchange/betting/rest/v1.0/")
        self.config = config
        self.app_key = self.config.BETFAIR_APP_KEY
        self.session_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def _extract_race_number(self, name: Optional[str]) -> int:
        """Extracts a race number from a market name, e.g., 'R1 1m Hcap'."""
        if not name: return 1 # Default to 1 if name is missing
        match = re.search(r'\bR(\d{1,2})\b', name)
        if match:
            num = int(match.group(1))
            return max(1, min(num, 20)) # Clamp to valid range 1-20
        return 1 # Default if no pattern is found

    async def _authenticate(self, http_client: httpx.AsyncClient):
        if self.session_token and self.token_expiry and self.token_expiry > datetime.now():
            return # Token is still valid

        auth_url = "https://identitysso.betfair.com/api/login"
        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'username={self.config.BETFAIR_USERNAME}&password={self.config.BETFAIR_PASSWORD}'

        log.info("BetfairAdapter: Authenticating to get new session token...")
        try:
            response = await http_client.post(auth_url, headers=headers, content=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'SUCCESS':
                self.session_token = data.get('token')
                self.token_expiry = datetime.now() + timedelta(hours=3)
                log.info("BetfairAdapter: Authentication successful.")
            else:
                raise Exception(f"Authentication failed: {data.get('error')}")
        except Exception as e:
            log.error("BetfairAdapter: Authentication failed catastrophically", error=str(e))
            raise

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            await self._authenticate(http_client)
            headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}

            # 1. Find all horse racing WIN markets for the day
            market_filter = {
                "eventTypeIds": ["7"], # 7 is Horse Racing
                "marketTypeCodes": ["WIN"],
                "marketStartTime": {"from": f"{date}T00:00:00Z", "to": f"{date}T23:59:59Z"}
            }
            market_catalogue = await self.make_request(http_client, 'POST', 'listMarketCatalogue/', headers=headers, json={"filter": market_filter, "maxResults": 1000, "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]})

            if not market_catalogue:
                return self._format_response([], start_time, is_success=True, error_message="No markets found.")

            all_races = []
            for market in market_catalogue:
                parsed_race = self._parse_race(market)
                all_races.append(parsed_race)

            return self._format_response(all_races, start_time)

        except Exception as e:
            log.error("BetfairAdapter: Failed to fetch races", exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    def _parse_race(self, market: Dict[str, Any]) -> Race:
        """Parses a single market from the catalogue into a Race object."""
        runners = []
        for runner_data in market.get('runners', []):
            # The catalogue doesn't have live odds, just runner info.
            # A full LiveOddsMonitor would now take the marketId and call listMarketBook.
            runners.append(Runner(
                number=runner_data.get('sortPriority', 0), # Using sortPriority as a proxy for number
                name=runner_data['runnerName']
            ))

        race_number = self._extract_race_number(market.get('marketName'))

        return Race(
            id=f"bf_{market['marketId']}",
            venue=market['event']['venue'],
            race_number=race_number,
            start_time=datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00')),
            runners=runners,
            source=self.source_name
        )

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': [r.model_dump() for r in races],
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }