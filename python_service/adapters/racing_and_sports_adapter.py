# python_service/adapters/racing_and_sports_adapter.py

import os
from datetime import datetime, timezone
from typing import Dict, Any

import aiohttp

from ..models import RaceData, RunnerData
from .base import BaseAdapter

class RacingAndSportsAdapter(BaseAdapter):
    """
    An adapter for fetching race data from the Racing and Sports API.
    """
    SOURCE_ID = "racing_and_sports"
    BASE_URL = "https://api.racingandsports.com.au/Meetings"

    def __init__(self):
        """Initializes the adapter and retrieves the necessary API key."""
        super().__init__()
        self.api_key = os.getenv("RAS_API_KEY")

    async def fetch_races(self) -> Dict[str, Any]:
        """
        Asynchronously fetches race data from the Racing and Sports API.
        """
        if not self.api_key:
            self.logger.error("RAS_API_KEY is not set. Cannot fetch data.")
            return {"races": [], "error": "ConfigurationError: RAS_API_KEY not set"}

        try:
            session = await self.get_session()
            headers = {"X-API-Key": self.api_key}
            async with session.get(self.BASE_URL, headers=headers, timeout=20) as response:
                response.raise_for_status()
                meetings_data = await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching RAS data: {e}")
            return {"races": [], "error": f"AIOHTTP Error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred fetching RAS data: {e}")
            return {"races": [], "error": f"Unexpected Error: {e}"}

        if not isinstance(meetings_data, list):
            return {"races": [], "error": "InvalidResponse: API did not return a list of meetings"}

        races = []
        for meeting in meetings_data:
            track_name = meeting.get('Venue', 'Unknown RAS Track')
            for race_data in meeting.get('Races', []):
                try:
                    post_time_str = race_data.get('StartTimeUTC')
                    if not post_time_str:
                        continue
                    post_time = datetime.fromisoformat(post_time_str.replace('Z', '+00:00'))

                    if post_time < datetime.now(timezone.utc):
                        continue

                    runners = [RunnerData(name=f"Runner #{r.get('RunnerNo')}", odds=None) for r in race_data.get('Runners', [])]
                    if not runners:
                        continue

                    races.append(RaceData(
                        race_id=f"ras_{race_data.get('RaceID')}",
                        track_name=track_name,
                        race_number=race_data.get('RaceNo'),
                        post_time=post_time,
                        runners=runners,
                        source=self.SOURCE_ID
                    ))
                except Exception as e:
                    self.logger.warning(f"Skipping malformed RAS race: {e}")

        return {"races": races}