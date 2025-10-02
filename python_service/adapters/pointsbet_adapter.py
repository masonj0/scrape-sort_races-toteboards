# python_service/adapters/pointsbet_adapter.py

import logging
import requests
from datetime import datetime
from typing import List

from ..models import RaceData, RunnerData
from .utils import parse_odds

class PointsBetAdapter:
    """
    Adapter for the PointsBet API, enhanced for multi-sport coverage.
    """
    SOURCE_ID = "pointsbet"
    API_TEMPLATE = "https://api.nj.pointsbet.com/api/v2/sports/{sport}/events/upcoming?page=1"
    SPORTS = ["horse-racing", "harness-racing", "greyhound-racing"]

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"GET request to {url} failed: {e}")
            return None

    def fetch_races(self) -> List[RaceData]:
        """
        Fetches race data for all configured sports from the PointsBet API.
        """
        self.logger.info("Fetching from PointsBet for all T/H/G sports...")
        all_races = []
        for sport in self.SPORTS:
            url = self.API_TEMPLATE.format(sport=sport)
            response_data = self._fetch_data(url)
            if not response_data or not isinstance(response_data, dict):
                self.logger.warning(f"Invalid response from PointsBet for sport: {sport}")
                continue

            parsed_races = self._parse_events(response_data.get('events', []), sport)
            all_races.extend(parsed_races)

        self.logger.info(f"Successfully fetched {len(all_races)} total races from PointsBet.")
        return all_races

    def _parse_events(self, events: List[dict], sport_name: str) -> List[RaceData]:
        """
        Parses a list of event dictionaries from the API response into Race objects.
        """
        races = []
        for event in events:
            try:
                if not event.get('winPlaceOddsAvailable'):
                    continue

                runners = []
                for outcome in event.get('fixedPrice', {}).get('outcomes', []):
                    if outcome.get('outcomeType') == 'Win':
                        odds = parse_odds(outcome.get('price'))
                        if odds is not None and odds < 999.0:
                            runners.append(RunnerData(name=outcome.get('name', 'Unknown'), odds=odds))

                if len(runners) < 3:
                    continue

                start_time_str = event.get('startsAt')
                if not start_time_str:
                    continue
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

                races.append(
                    RaceData(
                        race_id=f"pointsbet_{event.get('key', 'unknown')}",
                        track_name=event.get('competitionName', 'Unknown Track'),
                        race_number=event.get('eventNumber'),
                        post_time=start_time,
                        runners=runners,
                        source=self.SOURCE_ID,
                    )
                )
            except (KeyError, TypeError) as e:
                self.logger.warning(f"Skipping malformed PointsBet event for sport {sport_name}: {e}")
                continue
        return races