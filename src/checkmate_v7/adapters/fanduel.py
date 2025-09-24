from typing import List, Optional
from datetime import datetime, date
import logging
import json

from ..base import BaseAdapterV7
from ..models import Race, Runner


class FanDuelApiAdapterV7(BaseAdapterV7):
    """
    Adapter for the FanDuel GraphQL API.
    This version uses the 'GetRacingSchedule' query, which is believed to be
    more reliable than the previous queries.
    """
    SOURCE_ID = "fanduel_api"
    API_URL = "https://api.racing.fanduel.com/cosmo/v1/graphql"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    RACING_SCHEDULE_QUERY = {
        "operationName": "GetRacingSchedule",
        "variables": {
            "input": {
                "product": "FAN_DUEL_RACING",
                "jurisdiction": "USA"
            }
        },
        "query": "query GetRacingSchedule($input: RacingScheduleInput!) { racingSchedule(input: $input) { schedule { date tracks { id name races { id raceNumber postTime status runners { id runnerNumber runnerName scratched } } } } } }"
    }

    def fetch_races(self) -> List[Race]:
        """
        Fetches the entire racing schedule from the FanDuel GraphQL endpoint.
        """
        try:
            response_data = self.fetcher.post(
                self.API_URL,
                json_data=self.RACING_SCHEDULE_QUERY,
                headers=self.HEADERS,
                response_type='json'
            )
            if not response_data:
                logging.warning(f"{self.SOURCE_ID}: Did not receive a valid response from the API.")
                return []

            return self._parse_races(response_data)

        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to fetch or parse races: {e}", exc_info=True)
            return []

    def _parse_races(self, response_data: dict) -> List[Race]:
        """
        Parses the JSON data from the 'GetRacingSchedule' query into a list of
        standardized V7 Race objects.

        NOTE: This query does not provide odds, jockey, or trainer information.
        The resulting Race objects will be missing this data.
        """
        all_races = []
        try:
            tracks = response_data.get("data", {}).get("scheduleRaces", [])
            for track in tracks:
                for race_info in track.get("races", []):
                    # The track name is nested inside the race_info object
                    track_name = race_info.get("track", {}).get("name")

                    race = Race(
                        race_id=race_info.get("id"),
                        track_name=track_name,
                        race_number=int(race_info.get("number")),
                        post_time=self._to_datetime(race_info.get("postTime")),
                        race_type="Thoroughbred", # Assumption
                        number_of_runners=0, # Not available in this query
                        runners=[], # Not available in this query
                    )
                    all_races.append(race)
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed during parsing of race data: {e}", exc_info=True)
            return []

        return all_races

    def _to_datetime(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            # Example timestamp: "2025-09-22T20:05:00Z"
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            logging.warning(f"Could not parse timestamp: {timestamp_str}")
            return None
