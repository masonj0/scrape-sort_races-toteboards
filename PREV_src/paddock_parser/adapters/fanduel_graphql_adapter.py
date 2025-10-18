from datetime import datetime
from typing import Dict, List, Optional

from ..sync_fetcher import post_page_content
from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner

class FanDuelGraphQLAdapter(BaseAdapterV3):
    """
    Adapter for the FanDuel GraphQL API.
    This adapter is synchronous and uses the requests-based sync_fetcher.
    """
    SOURCE_ID = "fanduel"
    BASE_URL = "https://sb-prod-df.sportsbook.fanduel.com/api/v2/horse-racing/races"

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__(cache_dir)

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches data from the FanDuel GraphQL API.
        This is a synchronous operation wrapped in an async method.
        """
        graphql_query = {
            "query": """
                query AllRaces($first: Int!, $next: String) {
                    allRaces(first: $first, after: $next) {
                        edges {
                            node {
                                trackName
                                raceNumber
                                postTime
                                runners {
                                    runnerName
                                    odds
                                    scratched
                                }
                            }
                        }
                    }
                }
            """,
            "variables": {"first": 100}
        }

        try:
            raw_data = post_page_content(self.BASE_URL, post_data=graphql_query)
            return self.parse_races(raw_data)
        except Exception:
            return []

    def parse_races(self, raw_data: Dict) -> List[NormalizedRace]:
        """Parses the JSON response from the GraphQL API."""
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

                runners.append(
                    NormalizedRunner(
                        name=runner_data.get("runnerName"),
                        odds=self._to_float_odds(runner_data.get("odds")),
                        program_number=0
                    )
                )

            post_time = self._to_datetime(node.get("postTime"))

            races.append(
                NormalizedRace(
                    race_id=f"{node.get('trackName')}_{node.get('raceNumber')}",
                    track_name=node.get("trackName"),
                    race_number=node.get("raceNumber"),
                    post_time=post_time,
                    number_of_runners=len(runners),
                    runners=runners
                )
            )
        return races

    def _to_float_odds(self, odds_str: Optional[str]) -> Optional[float]:
        if not odds_str or "/" not in odds_str:
            return None
        try:
            num, den = map(int, odds_str.split('/'))
            return (num / den) + 1.0
        except (ValueError, ZeroDivisionError):
            return None

    def _to_datetime(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
