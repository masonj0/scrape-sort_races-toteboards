import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..base import BaseAdapterV3, NormalizedRace
from ..http_client import ForagerClient

class RasAdapter(BaseAdapterV3):
    """
    Adapter for the Racing and Sports (RAS) JSON feed.
    This adapter fetches and parses multi-discipline (Thoroughbred, Harness, Greyhound)
    race data from a single endpoint.
    """

    SOURCE_ID = "ras"
    BASE_URL = "https://www.racingandsports.com.au"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.forager = ForagerClient()

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches the JSON data from the RAS endpoint and parses it.
        """
        url = f"{self.BASE_URL}/todays-racing-json-v2"
        json_text = await self.forager.fetch(url)
        if not json_text:
            logging.error(f"Failed to fetch data from {url}")
            return []
        return self.parse_races(json_text)

    def parse_races(self, json_text: str) -> List[NormalizedRace]:
        """
        Parses the JSON response from the RAS endpoint into a list of NormalizedRace objects.
        """
        races = []
        if not json_text:
            return races

        try:
            payload = json.loads(json_text)
            for discipline_group in payload or []:
                for country_group in discipline_group.get("Countries", []):
                    for meeting in country_group.get("Meetings", []):
                        course = (meeting.get("Course") or "").strip()
                        if not course:
                            continue

                        race_number = int(meeting.get("RaceNumber", 0))

                        races.append(
                            NormalizedRace(
                                race_id=f"{self.SOURCE_ID}-{course}-{race_number}",
                                track_name=course,
                                race_number=race_number,
                                number_of_runners=0,
                                runners=[]
                            )
                        )
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from RAS feed: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while parsing RAS data: {e}")

        return races
