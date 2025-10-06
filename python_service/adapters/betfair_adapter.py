#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Betfair API Adapter (v2 - Live Odds Enabled)
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
    """API client for the Betfair Exchange, with live odds capability."""

    def __init__(self, config):
        super().__init__(source_name="BetfairExchange", base_url="https://api.betfair.com/exchange/betting/rest/v1.0/")
        self.config = config
        self.app_key = self.config.BETFAIR_APP_KEY
        self.session_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    async def _authenticate(self, http_client: httpx.AsyncClient):
        if self.session_token and self.token_expiry and self.token_expiry > datetime.now():
            return
        if not all([self.app_key, self.config.BETFAIR_USERNAME, self.config.BETFAIR_PASSWORD]):
            raise ValueError("Betfair credentials not fully configured.")

        auth_url = "https://identitysso.betfair.com/api/login"
        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'username={self.config.BETFAIR_USERNAME}&password={self.config.BETFAIR_PASSWORD}'

        log.info("BetfairAdapter: Authenticating...")
        response = await http_client.post(auth_url, headers=headers, content=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'SUCCESS':
            self.session_token = data.get('token')
            self.token_expiry = datetime.now() + timedelta(hours=3)
        else:
            raise ConnectionError(f"Betfair authentication failed: {data.get('error')}")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            await self._authenticate(http_client)
            headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}
            market_filter = {"eventTypeIds": ["7"], "marketTypeCodes": ["WIN"], "marketStartTime": {"from": f"{date}T00:00:00Z", "to": f"{date}T23:59:59Z"}}

            response = await http_client.post(self.base_url + 'listMarketCatalogue/', headers=headers, json={"filter": market_filter, "maxResults": 1000, "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]})
            response.raise_for_status()
            market_catalogue = response.json()

            if not market_catalogue:
                return self._format_response([], start_time, is_success=True, error_message="No markets found.")

            all_races = [self._parse_race(market) for market in market_catalogue]
            return self._format_response(all_races, start_time, is_success=True)
        except Exception as e:
            log.error("BetfairAdapter: Failed to fetch races", exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    async def get_live_odds_for_market(self, market_id: str, http_client: httpx.AsyncClient) -> Dict[int, Decimal]:
        """TACTICAL method (Pillar 3). Gets live LTP for each runner in a market."""
        log.info("BetfairAdapter: Fetching live odds for market", market_id=market_id)
        await self._authenticate(http_client)
        headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}

        # This is a REST endpoint, so the params are sent directly as the JSON body.
        params = {"marketIds": [market_id], "priceProjection": {"priceData": ["EX_TRADED"]}}
        response = await http_client.post(self.base_url + 'listMarketBook/', headers=headers, json=params)
        response.raise_for_status()
        market_book = response.json()

        live_odds = {}
        if market_book and market_book[0].get('runners'):
            for runner in market_book[0]['runners']:
                if runner.get('status') == 'ACTIVE' and runner.get('lastPriceTraded'):
                    live_odds[runner['selectionId']] = Decimal(str(runner['lastPriceTraded']))
        return live_odds

    def _parse_race(self, market: Dict[str, Any]) -> Race:
        runners = []
        for runner_data in market.get('runners', []):
            runners.append(Runner(
                number=runner_data.get('sortPriority', 99),
                name=runner_data['runnerName'],
                selection_id=runner_data['selectionId']
            ))
        return Race(
            id=f"bf_{market['marketId']}",
            venue=market['event']['venue'],
            race_number=self._extract_race_number(market.get('marketName')),
            start_time=datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00')),
            runners=runners,
            source=self.source_name
        )

    def _extract_race_number(self, name: Optional[str]) -> int:
        if not name: return 1
        match = re.search(r'\\bR(\\d{1,2})\\b', name)
        return int(match.group(1)) if match else 1

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }