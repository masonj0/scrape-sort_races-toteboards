# python_service/adapters/betfair_adapter.py

import logging
from datetime import datetime
from typing import List

from .base import BaseAdapterV7, Race, Runner
from .utils import parse_odds

class BetfairExchangeAdapter(BaseAdapterV7):
    """
    Adapter for the Betfair Exchange API.
    """
    SOURCE_ID = "betfair_exchange"
    API_ENDPOINT = "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?alt=json&filter=canonical&maxResults=25&rollupLimit=2&types=EVENT,MARKET_DESCRIPTION,RUNNER_DESCRIPTION,RUNNER_EXCHANGE_PRICES_BEST,MARKET_STATE&marketProjection=EVENT,MARKET_START_TIME,RUNNER_DESCRIPTION&eventTypeIds=7"

    def fetch_races(self) -> List[Race]:
        """
        Fetches race data from the Betfair Exchange API and transforms it into
        the standardized Race model.
        """
        data = self.fetcher.get(self.API_ENDPOINT, headers={'Accept': 'application/json'})
        if not isinstance(data, dict):
            logging.warning(f"BetfairExchangeAdapter received invalid or non-dict data: {type(data)}")
            return []

        return self._parse_betfair_races(data)

    def _parse_betfair_races(self, data: dict) -> List[Race]:
        """
        Parses the complex JSON structure from the Betfair API.
        """
        races = []
        try:
            event_nodes = data.get('eventTypes', [{}])[0].get('eventNodes', [])
            for event_node in event_nodes:
                event = event_node.get('event', {})
                for market_node in event_node.get('marketNodes', []):
                    market = market_node.get('market', {})
                    if market.get('marketType', '') != 'WIN':
                        continue

                    runners = []
                    for runner_node in market_node.get('runners', []):
                        if runner_node.get('state', {}).get('status') != 'ACTIVE':
                            continue

                        raw_odds = None
                        if 'exchange' in runner_node:
                            available_to_back = runner_node['exchange'].get('availableToBack', [])
                            if available_to_back:
                                raw_odds = available_to_back[0].get('price')

                        # Use the centralized utility to parse odds.
                        # The raw_odds is already a float here, but using the utility ensures consistency.
                        odds = parse_odds(raw_odds)

                        if odds < 999.0:
                            runners.append(
                                Runner(
                                    name=runner_node.get('description', {}).get('runnerName', 'Unknown'),
                                    odds=odds
                                )
                            )

                    if len(runners) >= 3:
                        start_time = None
                        if market.get('marketStartTime'):
                            try:
                                start_time = datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00'))
                            except ValueError:
                                pass # Ignore if parsing fails

                        race_number = None
                        event_name = event.get('eventName', '')
                        if 'R' in event_name:
                            try:
                                race_number = int(event_name.split('R')[-1])
                            except (ValueError, IndexError):
                                pass

                        races.append(
                            Race(
                                race_id=f"betfair_{market.get('marketId', 'unknown')}",
                                track_name=event.get('venue', 'Betfair Exchange'),
                                post_time=start_time,
                                race_number=race_number,
                                runners=runners,
                                source=self.SOURCE_ID
                            )
                        )
        except (KeyError, TypeError, IndexError) as e:
            logging.error(f"Error parsing Betfair data structure: {e}")

        return races