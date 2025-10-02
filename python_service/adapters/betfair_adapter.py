# python_service/adapters/betfair_adapter.py

import os
from .base import BaseAdapter
from ..models import RaceData, RunnerData
from typing import List, Dict, Any
from datetime import datetime, timezone

class BetfairAdapter(BaseAdapter):
    """Adapter for the Betfair Exchange API, inspired by the Data Scientist adapter."""
    SOURCE_ID = "betfair_exchange"
    BASE_URL = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    def __init__(self, fetcher):
        super().__init__(fetcher)
        self.app_key = os.getenv("BETFAIR_APP_KEY")
        self.session_token = os.getenv("BETFAIR_SESSION_TOKEN")

    def fetch_races(self) -> List[RaceData]:
        if not self.app_key or not self.session_token:
            self.logger.warning(f"API keys for {self.SOURCE_ID} not configured. Skipping.")
            return []

        self.logger.info(f"Fetching market catalogues from {self.SOURCE_ID}")
        headers = {
            "X-Application": self.app_key,
            "X-Authentication": self.session_token,
            "Content-Type": "application/json"
        }
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketCatalogue",
            "params": {
                "filter": {"eventTypeIds": ["7"], "marketTypeCodes": ["WIN"]},
                "maxResults": 100,
                "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]
            },
            "id": 1
        }

        response_data = self.fetcher.post(self.BASE_URL, headers=headers, json=payload)
        if not response_data or "result" not in response_data:
            self.logger.error("Invalid or empty response from Betfair API.")
            return []

        races = []
        for market in response_data["result"]:
            try:
                runners = [RunnerData(name=r['runnerName'], odds=None) for r in market.get('runners', [])]
                # Note: This endpoint does not provide live odds. A second call to listMarketBook would be needed.
                races.append(RaceData(
                    race_id=f"bf_{market['marketId']}",
                    track_name=market.get('event', {}).get('venue', 'Unknown Track'),
                    post_time=datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00')),
                    runners=runners,
                    source=self.SOURCE_ID
                ))
            except (KeyError, TypeError) as e:
                self.logger.warning(f"Skipping malformed Betfair market: {e}")

        return races