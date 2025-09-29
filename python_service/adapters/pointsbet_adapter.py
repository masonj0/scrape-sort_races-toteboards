# python_service/adapters/pointsbet_adapter.py

import logging
from datetime import datetime
from typing import List

from .base import BaseAdapterV7, Race, Runner
from .utils import parse_odds

class PointsBetAdapter(BaseAdapterV7):
    """
    Adapter for the PointsBet API.
    """
    SOURCE_ID = "pointsbet"
    BASE_URL = "https://api.nj.pointsbet.com/api/v2/sports/horse-racing/events/upcoming?page=1"

    def fetch_races(self) -> List[Race]:
        """
        Fetches race data from the PointsBet API and transforms it into the
        standardized Race model.
        """
        response_data = self.fetcher.get(self.BASE_URL)
        if not isinstance(response_data, dict) or not response_data.get('events'):
            logging.warning(f"PointsBetAdapter received invalid or non-dict data: {type(response_data)}")
            return []

        races = []
        for event in response_data['events']:
            try:
                if not event.get('winPlaceOddsAvailable'):
                    continue

                runners = []
                for outcome in event.get('fixedPrice', {}).get('outcomes', []):
                    if outcome.get('outcomeType') == 'Win':
                        # Use the centralized utility to parse odds
                        odds = parse_odds(outcome.get('price'))
                        if odds < 999.0:
                            runners.append(Runner(name=outcome.get('name', 'Unknown'), odds=odds))

                if len(runners) < 3:
                    continue

                start_time = datetime.fromisoformat(event['startsAt'].replace('Z', '+00:00')) if event.get('startsAt') else None

                races.append(
                    Race(
                        race_id=f"pointsbet_{event.get('key', 'unknown')}",
                        track_name=event.get('competitionName', 'Unknown Track'),
                        race_number=event.get('eventNumber'),
                        post_time=start_time,
                        runners=runners,
                        source=self.SOURCE_ID
                    )
                )
            except (KeyError, TypeError) as e:
                logging.warning(f"Skipping malformed PointsBet event: {e}")
                continue

        return races