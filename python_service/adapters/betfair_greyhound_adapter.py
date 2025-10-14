# python_service/adapters/betfair_greyhound_adapter.py
from datetime import datetime, timedelta
from typing import AsyncGenerator
from decimal import Decimal

from ..models import Race, Runner, OddsData
from .base import BaseAdapter
from .betfair_auth_mixin import BetfairAuthMixin

class BetfairGreyhoundAdapter(BetfairAuthMixin, BaseAdapter):
    """Adapter for fetching greyhound racing data from the Betfair Exchange API."""

    SOURCE_NAME = "BetfairGreyhounds"
    BASE_URL = "https://api.betfair.com/exchange/betting/rest/v1.0/"

    def __init__(self, config=None):
        super().__init__(self.SOURCE_NAME, self.BASE_URL)
        if config:
            self.betfair_app_key = config.BETFAIR_APP_KEY
            self.betfair_username = config.BETFAIR_USERNAME
            self.betfair_password = config.BETFAIR_PASSWORD

    async def fetch_races(self, date: str, http_client) -> AsyncGenerator[Race, None]:
        """Fetches all greyhound races for a given date."""
        await self._authenticate(http_client)
        if not self.session_token:
            # self.logger.error("Authentication failed, cannot fetch races.")
            return

        start_time, end_time = self._get_datetime_range(date)

        market_catalogue = await self.make_request(
            http_client=http_client,
            method="post",
            url=f"{self.BASE_URL}listMarketCatalogue/",
            json={
                "filter": {
                    "eventTypeIds": ["4339"],  # Greyhound Racing
                    "marketCountries": ["GB", "IE"],
                    "marketTypeCodes": ["WIN"],
                    "marketStartTime": {"from": start_time.isoformat() + "Z", "to": end_time.isoformat() + "Z"}
                },
                "maxResults": 1000,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            }
        )

        if not market_catalogue:
            return

        for market in market_catalogue:
            yield await self._parse_race(market, http_client)

    async def _parse_race(self, market: dict, http_client) -> Race:
        """Parses a single market from the Betfair API into a Race object."""
        market_id = market['marketId']
        event = market['event']
        start_time = datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00'))

        odds_data = await self._get_odds_for_market(market_id, http_client)

        runners = [
            Runner(
                number=runner.get('sortPriority', i + 1),
                name=runner['runnerName'],
                scratched=runner['status'] != 'ACTIVE',
                selection_id=runner['selectionId'],
                odds=odds_data.get(runner['selectionId'], {})
            )
            for i, runner in enumerate(market.get('runners', []))
        ]

        return Race(
            id=f"bfg_{market_id}",
            venue=event.get('venue', 'Unknown Venue'),
            race_number=self._extract_race_number(market.get('marketName', '')),
            start_time=start_time,
            runners=runners,
            source=self.SOURCE_NAME
        )

    async def _get_odds_for_market(self, market_id: str, http_client) -> dict:
        """Fetches the latest odds for a given market."""
        market_book = await self.make_request(
            http_client=http_client,
            method="post",
            url=f"{self.BASE_URL}listMarketBook/",
            json={
                "marketIds": [market_id],
                "priceProjection": {
                    "priceData": ["EX_BEST_OFFERS"]
                }
            }
        )

        odds_data = {}
        if market_book and market_book[0].get('runners'):
            for runner in market_book[0]['runners']:
                selection_id = runner['selectionId']
                if runner['status'] == 'ACTIVE' and runner['ex']['availableToBack']:
                    win_odds = Decimal(str(runner['ex']['availableToBack'][0]['price']))
                    odds_data[selection_id] = {
                        self.SOURCE_NAME: OddsData(
                            win=win_odds,
                            source=self.SOURCE_NAME,
                            last_updated=datetime.now()
                        )
                    }
        return odds_data

    def _get_datetime_range(self, date_str: str):
        start_of_day = datetime.strptime(date_str, "%Y-%m-%d")
        end_of_day = start_of_day + timedelta(days=1)
        return start_of_day, end_of_day

    def _extract_race_number(self, market_name: str) -> int:
        import re
        match = re.search(r"R(\d+)", market_name)
        return int(match.group(1)) if match else 0