# python_service/adapters/racing_and_sports_adapter.py

import os
import logging
import requests
from typing import List, Optional
from datetime import datetime, timezone

from ..models import RaceData

class RacingAndSportsAdapter:
    """
    Adapter for the RacingAndSports API, enhanced for multi-race type coverage.
    """
    SOURCE_ID = "ras"
    API_TEMPLATE = "https://api.racingandsports.com.au/Meetings?RaceType={race_type}"
    RACE_TYPES = ['R', 'G', 'H']  # R=Thoroughbred, G=Greyhound, H=Harness

    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_key = api_key or os.getenv("RAS_API_KEY")

    def _fetch_data(self, url, headers):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"GET request to {url} failed: {e}")
            return None

    def fetch_races(self) -> List[RaceData]:
        if not self.api_key:
            self.logger.warning("RAS_API_KEY not configured. Skipping RacingAndSports.")
            return []

        self.logger.info("Fetching from RacingAndSports for all T/H/G race types...")
        all_races: List[RaceData] = []
        headers = {"X-API-Key": self.api_key}

        for race_type in self.RACE_TYPES:
            url = self.API_TEMPLATE.format(race_type=race_type)
            meetings_data = self._fetch_data(url, headers=headers)
            if not meetings_data or not isinstance(meetings_data, list):
                self.logger.warning(f"Invalid or empty response from RAS for race type: {race_type}")
                continue

            races = self._parse_meetings(meetings_data, race_type)
            all_races.extend(races)

        self.logger.info(f"Successfully fetched {len(all_races)} total races from RacingAndSports.")
        return all_races

    def _parse_meetings(self, meetings: List[dict], race_type: str) -> List[RaceData]:
        """
        Parses a list of meetings to extract individual races.
        """
        parsed_races = []
        for meeting in meetings:
            track_name = meeting.get('Venue', 'Unknown Track')
            for race_data in meeting.get('Races', []):
                try:
                    post_time_str = race_data.get('StartTimeUTC', '')
                    if not post_time_str:
                        continue
                    post_time = datetime.fromisoformat(post_time_str.replace('Z', '+00:00'))

                    if post_time < datetime.now(timezone.utc):
                        continue

                    placeholder_race = RaceData(
                        race_id=f"ras_{race_data.get('RaceID')}",
                        track_name=track_name,
                        race_number=race_data.get('RaceNo'),
                        post_time=post_time,
                        runners=[],
                        source=self.SOURCE_ID,
                    )
                    parsed_races.append(placeholder_race)
                except (KeyError, TypeError, ValueError) as e:
                    self.logger.warning(f"Skipping malformed RAS race: {e}")
                    continue
        return parsed_races