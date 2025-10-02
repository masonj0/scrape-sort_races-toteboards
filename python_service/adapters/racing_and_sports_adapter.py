# python_service/adapters/racing_and_sports_adapter.py

import os
import logging
from datetime import datetime, timezone
from ..models import RaceData, RunnerData
from .base import BaseAdapter

class RacingAndSportsAdapter(BaseAdapter):
    SOURCE_ID = "racing_and_sports"
    BASE_URL = "https://api.racingandsports.com.au/Meetings"

    def __init__(self, fetcher):
        super().__init__(fetcher)
        self.api_key = os.getenv("RAS_API_KEY")

    def fetch_races(self):
        if not self.api_key:
            return {'success': False, 'error_details': {'error': 'ConfigurationError', 'message': 'RAS_API_KEY not set'}}

        fetch_result = self.fetcher.get(self.BASE_URL, headers={"X-API-Key": self.api_key}, source_id=self.SOURCE_ID)
        if not fetch_result['success']:
            return {'success': False, 'error_details': fetch_result}

        meetings_data = fetch_result['data']
        if not isinstance(meetings_data, list):
            return {'success': False, 'error_details': {'error': 'InvalidResponse', 'message': 'API did not return a list of meetings'}}

        races = []
        for meeting in meetings_data:
            track_name = meeting.get('Venue', 'Unknown RAS Track')
            for race_data in meeting.get('Races', []):
                try:
                    post_time_str = race_data.get('StartTimeUTC')
                    if not post_time_str: continue
                    post_time = datetime.fromisoformat(post_time_str.replace('Z', '+00:00'))
                    if post_time < datetime.now(timezone.utc): continue

                    runners = [RunnerData(name=f"Runner #{r.get('RunnerNo')}", odds=None) for r in race_data.get('Runners', [])]
                    if not runners: continue

                    races.append(RaceData(
                        race_id=f"ras_{race_data.get('RaceID')}", track_name=track_name,
                        race_number=race_data.get('RaceNo'), post_time=post_time,
                        runners=runners, source=self.SOURCE_ID
                    ))
                except Exception as e:
                    self.logger.warning(f"Skipping malformed RAS race: {e}")

        return {'success': True, 'data': races}