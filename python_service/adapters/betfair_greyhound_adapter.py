# python_service/adapters/betfair_greyhound_adapter.py
from datetime import datetime
from typing import Any, List

from ..models import Race, Runner
from .base_v3 import BaseAdapterV3
from .betfair_auth_mixin import BetfairAuthMixin

class BetfairGreyhoundAdapter(BetfairAuthMixin, BaseAdapterV3):
    """Adapter for fetching greyhound racing data from the Betfair Exchange API, using V3 architecture."""

    SOURCE_NAME = "BetfairGreyhounds"
    BASE_URL = "https://api.betfair.com/exchange/betting/rest/v1.0/"

    async def _fetch_data(self, date: str) -> Any:
        """Fetches the raw market catalogue for greyhound races on a given date."""
        await self._authenticate()
        if not self.session_token:
            self.logger.error("Authentication failed, cannot fetch data.")
            return None

        start_time, end_time = self._get_datetime_range(date)

        return await self.make_request(
            method="post",
            url=f"{self.BASE_URL}listMarketCatalogue/",
            json={
                "filter": {
                    "eventTypeIds": ["4339"],  # Greyhound Racing
                    "marketCountries": ["GB", "IE", "AU"],
                    "marketTypeCodes": ["WIN"],
                    "marketStartTime": {"from": start_time.isoformat(), "to": end_time.isoformat()}
                },
                "maxResults": 1000,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            }
        )

    def _parse_races(self, raw_data: Any) -> List[Race]:
        """Parses the raw market catalogue into a list of Race objects."""
        if not raw_data:
            return []

        races = []
        for market in raw_data:
            try:
                races.append(self._parse_race(market))
            except (KeyError, TypeError):
                self.logger.warning("Failed to parse a Betfair Greyhound market.", exc_info=True, market=market)
                continue
        return races

    def _parse_race(self, market: dict) -> Race:
        """Parses a single market from the Betfair API into a Race object."""
        market_id = market['marketId']
        event = market['event']
        start_time = datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00'))

        runners = [
            Runner(
                number=runner.get('sortPriority', i + 1),
                name=runner['runnerName'],
                scratched=runner['status'] != 'ACTIVE',
                selection_id=runner['selectionId']
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