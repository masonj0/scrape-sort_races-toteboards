# python_service/adapters/betfair_adapter.py

import os
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import httpx
from decimal import Decimal

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

class BetfairAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            source_name="Betfair",
            base_url="https://api.betfair.com/exchange/betting/json-rpc/v1"
        )
        self.app_key = os.getenv("BETFAIR_APP_KEY")
        self.username = os.getenv("BETFAIR_USERNAME")
        self.password = os.getenv("BETFAIR_PASSWORD")
        self.session_token: str | None = None
        self.token_expiry: datetime | None = None

    async def _authenticate(self, http_client: httpx.AsyncClient):
        if self.session_token and self.token_expiry and self.token_expiry > datetime.now():
            return
        if not all([self.app_key, self.username, self.password]):
            raise Exception("Betfair credentials not set in environment.")

        auth_url = "https://identitysso.betfair.com/api/login"
        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'username={self.username}&password={self.password}'

        response = await http_client.post(auth_url, headers=headers, content=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'SUCCESS':
            self.session_token = data.get('token')
            self.token_expiry = datetime.now() + timedelta(hours=4)
        else:
            raise Exception(f"Betfair authentication failed: {data.get('error')}")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            await self._authenticate(http_client)

            market_filter = {
                "eventTypeIds": ["7"], "marketTypeCodes": ["WIN"],
                "marketStartTime": {"from": f"{date}T00:00:00Z", "to": f"{date}T23:59:59Z"}
            }
            headers = {"X-Application": self.app_key, "X-Authentication": self.session_token, "Content-Type": "application/json"}
            json_payload = {
                "jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue",
                "params": {
                    "filter": market_filter,
                    "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"],
                    "maxResults": 1000
                }, "id": 1
            }

            # BUG FIX: Use the resilient self.make_request method
            markets_response = await self.make_request(http_client, 'POST', '/', headers=headers, json=json_payload)
            if not markets_response or 'result' not in markets_response:
                return {'races': []}

            all_races = [self._parse_betfair_race(market) for market in markets_response['result']]
            fetch_duration = (datetime.now() - start_time).total_seconds()
            return {
                # FEEDBACK FIX: Use .model_dump() instead of .dict()
                'races': [r.model_dump() for r in all_races],
                'source_info': {
                    'name': self.source_name, 'status': 'SUCCESS',
                    'races_fetched': len(all_races), 'error_message': None,
                    'fetch_duration': fetch_duration
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to fetch races from Betfair: {e}", exc_info=True)
            raise

    def _parse_betfair_race(self, market: Dict[str, Any]) -> Race:
        venue = market.get('event', {}).get('venue', 'Unknown Venue')
        start_time = datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00'))

        # BUG FIX: Use a robust regex for race number parsing
        match = re.search(r'[Rr](\\d+)', market.get('marketName', ''))
        race_number = int(match.group(1)) if match else 0

        runners = []
        for runner_data in market.get('runners', []):
            if runner_data.get('status') == 'ACTIVE':
                runners.append(Runner(
                    number=runner_data.get('sortPriority', 0),
                    name=runner_data.get('runnerName', 'Unknown Runner'),
                    scratched=False # Explicitly set required field
                ))

        return Race(
            id=f"bf_{market['marketId']}",
            venue=venue, race_number=race_number, start_time=start_time,
            runners=runners,
            source=self.source_name # BUG FIX: Add the required 'source' field
        )