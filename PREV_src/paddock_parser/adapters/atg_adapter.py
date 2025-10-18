import httpx
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner

class AtgAdapter(BaseAdapterV3):
    """
    Adapter for the ATG GraphQL API.
    """
    SOURCE_ID = "atg"
    API_ENDPOINT = "https://www.atg.se/services/v1/games/"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches data from the ATG GraphQL API.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        game_id = f"V75_{today_str}"

        query = {
            "query": "query Game($gameId: String!) { game(id: $gameId) { id status races { id name startTime horses { id name money results { place } scratched } } } }",
            "variables": { "gameId": game_id }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.API_ENDPOINT, json=query, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                return self.parse_races(await response.json())
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Error fetching data from ATG: {e}")
            return []

    def parse_races(self, json_data: Dict[str, Any]) -> List[NormalizedRace]:
        """
        Parses the JSON response from the ATG API into a list of NormalizedRace objects.
        """
        races = []
        game_data = json_data.get("data", {}).get("game")
        if not game_data:
            return races

        for race_data in game_data.get("races", []):
            runners = []
            for horse_data in race_data.get("horses", []):
                if not horse_data.get("scratched"):
                    runners.append(
                        NormalizedRunner(
                            name=horse_data.get("name"),
                            program_number=0, # Not available in data
                        )
                    )

            if not runners:
                continue

            try:
                post_time = datetime.fromisoformat(race_data.get("startTime")).astimezone(timezone.utc)
            except (ValueError, TypeError):
                post_time = None

            races.append(
                NormalizedRace(
                    race_id=race_data.get("id"),
                    track_name="ATG", # Not available in data, using source name
                    race_number=0, # Not available in data
                    race_type=race_data.get("name"),
                    post_time=post_time,
                    number_of_runners=len(runners),
                    runners=runners,
                )
            )
        return races
