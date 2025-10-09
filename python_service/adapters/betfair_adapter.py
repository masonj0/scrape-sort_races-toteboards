# python_service/adapters/betfair_adapter.py

import httpx
import structlog
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import BaseAdapter
from .betfair_auth_mixin import BetfairAuthMixin
from ..models import Race, Runner

log = structlog.get_logger(__name__)

class BetfairAdapter(BetfairAuthMixin, BaseAdapter):
    def __init__(self, config):
        super().__init__(source_name="BetfairExchange", base_url="https://api.betfair.com/exchange/betting/rest/v1.0/")
        self.config = config
        self.app_key = self.config.BETFAIR_APP_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            await self._authenticate(http_client)
            headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}
            market_filter = {"eventTypeIds": ["7"], "marketTypeCodes": ["WIN"], "marketStartTime": {"from": f"{date}T00:00:00Z", "to": f"{date}T23:59:59Z"}}
            market_catalogue = await self.make_request(http_client, 'POST', 'listMarketCatalogue/', headers=headers, json={"filter": market_filter, "maxResults": 1000, "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]})
            if not market_catalogue:
                return self._format_response([], start_time, is_success=True, error_message="No markets found.")
            all_races = [self._parse_race(market) for market in market_catalogue]
            return self._format_response(all_races, start_time, is_success=True)
        except Exception as e:
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    def _parse_race(self, market: Dict[str, Any]) -> Race:
        runners = [Runner(number=rd.get('sortPriority', 99), name=rd['runnerName'], selection_id=rd['selectionId']) for rd in market.get('runners', [])]
        return Race(id=f"bf_{market['marketId']}", venue=market['event']['venue'], race_number=self._extract_race_number(market.get('marketName')), start_time=datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00')), runners=runners, source=self.source_name)

    def _extract_race_number(self, name: Optional[str]) -> int:
        if not name: return 1
        match = re.search(r'\\bR(\\d{1,2})\\b', name)
        return int(match.group(1)) if match else 1

    async def get_live_odds_for_market(self, market_id: str, http_client: httpx.AsyncClient) -> Dict[int, Decimal]:
        """TACTICAL method (Pillar 3). Gets live LTP for each runner in a market."""
        log.info("BetfairAdapter: Fetching live odds for market", market_id=market_id)
        try:
            await self._authenticate(http_client)
            headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}

            params = {"marketIds": [market_id], "priceProjection": {"priceData": ["EX_TRADED"]}}
            market_book = await self.make_request(
                http_client,
                'POST',
                'listMarketBook/',
                headers=headers,
                json=params
            )

            live_odds = {}
            if market_book and market_book[0].get('runners'):
                for runner in market_book[0]['runners']:
                    if runner.get('status') == 'ACTIVE' and runner.get('lastPriceTraded'):
                        live_odds[runner['selectionId']] = Decimal(str(runner['lastPriceTraded']))
            return live_odds
        except httpx.HTTPError as e:
            log.error("BetfairAdapter: Failed to get live odds", market_id=market_id, error=str(e), exc_info=True)
            return {} # Return empty dict on failure
        except Exception as e:
            log.error("BetfairAdapter: Unexpected error getting live odds", market_id=market_id, error=str(e), exc_info=True)
            return {} # Return empty dict on failure
