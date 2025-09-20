"""
The new, modern FanDuel API adapter.
"""
from typing import List, Optional
from datetime import datetime
import logging
import json

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner


class FanDuelApiAdapterV7(BaseAdapterV7):
    """
    Adapter for the FanDuel public API using a direct API endpoint.
    This is the modern implementation, intended to replace the GraphQL version.
    """
    SOURCE_ID = "fanduel_api"
    API_URL = "https://sb-prod-df.sportsbook.fanduel.com/api/v2/horse-racing/races"

    async def fetch_races(self) -> List[Race]:
        """Fetches data from the FanDuel API."""
        graphql_query = {
            "query": """
                query AllRaces($first: Int!, $next: String) {
                    allRaces(first: $first, after: $next) {
                        edges { node { trackName raceNumber postTime runners { runnerName odds { decimal } scratched } } }
                    }
                }
            """,
            "variables": {"first": 100}
        }
        try:
            # Using the fetcher from the base class
            raw_data = await self.fetcher.post(self.API_URL, json_data=graphql_query)
            if not raw_data:
                return []
            return self._parse_races(raw_data)
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to fetch or parse races: {e}")
            return []

    def _parse_races(self, raw_data: dict) -> List[Race]:
        """Parses the JSON response from the API."""
        races = []
        race_edges = raw_data.get("data", {}).get("allRaces", {}).get("edges", [])
        if not race_edges:
            return []

        for edge in race_edges:
            node = edge.get("node", {})
            if not node:
                continue

            runners = []
            for runner_data in node.get("runners", []):
                if runner_data.get('scratched'):
                    continue

                odds_obj = runner_data.get("odds")
                decimal_odds = odds_obj.get("decimal") if odds_obj else None

                runners.append(Runner(
                    name=runner_data.get("runnerName"),
                    odds=decimal_odds,
                    program_number=None  # Not provided in API
                ))

            post_time = self._to_datetime(node.get("postTime"))
            track_name = node.get('trackName')
            race_number = node.get('raceNumber')

            races.append(Race(
                race_id=f"{self.SOURCE_ID}_{track_name}_{race_number}",
                track_name=track_name,
                race_number=race_number,
                post_time=post_time,
                runners=runners
            ))
        return races

    def _to_datetime(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            # The timestamp is in ISO 8601 format with a 'Z' for UTC.
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
