from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List

import httpx
import structlog
from pydantic import ValidationError

from ..models import OddsData
from ..models import Race
from ..models import Runner
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class GreyhoundAdapter(BaseAdapter):
    """Adapter for fetching Greyhound racing data. Activated by setting GREYHOUND_API_URL in .env"""

    def __init__(self, config):
        if not config.GREYHOUND_API_URL:
            raise ValueError("GreyhoundAdapter cannot be initialized without GREYHOUND_API_URL.")
        super().__init__(source_name="Greyhound Racing", base_url=config.GREYHOUND_API_URL, config=config)
        # Example for future use: self.api_key = config.GREYHOUND_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Fetches upcoming greyhound races for the specified date."""
        start_time = datetime.now()
        endpoint = f"v1/cards/{date}"  # Using date parameter
        try:
            response = await self.make_request(http_client, "GET", endpoint)
            if not response:
                log.warning("GreyhoundAdapter: No response from make_request.")
                return self._format_response(
                    [], start_time, is_success=True, error_message="No data received from provider."
                )

            response_json = response.json()
            if not response_json or not response_json.get("cards"):
                log.warning("GreyhoundAdapter: No 'cards' in response or empty list.")
                return self._format_response(
                    [], start_time, is_success=True, error_message="No race cards found for date."
                )

            all_races = self._parse_cards(response_json["cards"])
            if not all_races:
                return self._format_response(
                    [], start_time, is_success=True, error_message="Races found, but none could be parsed."
                )

            return self._format_response(all_races, start_time, is_success=True)
        except httpx.HTTPError as e:
            log.error("GreyhoundAdapter: HTTP request failed after retries", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message="API request failed after multiple retries."
            )
        except Exception as e:
            log.error("GreyhoundAdapter: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message=f"An unexpected error occurred: {str(e)}"
            )

    def _format_response(
        self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None
    ) -> Dict[str, Any]:
        """Formats the adapter's response consistently."""
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            "races": races,
            "source_info": {
                "name": self.source_name,
                "status": "SUCCESS" if is_success else "FAILED",
                "races_fetched": len(races),
                "error_message": error_message,
                "fetch_duration": fetch_duration,
            },
        }

    def _parse_cards(self, cards: List[Dict[str, Any]]) -> List[Race]:
        """Parses a list of cards and their races into Race objects."""
        all_races = []
        if cards is None:
            return all_races
        for card in cards:
            venue = card.get("track_name", "Unknown Venue")
            races_data = card.get("races", [])
            for race_data in races_data:
                try:
                    if not race_data.get("runners"):
                        continue

                    race = Race(
                        id=f"greyhound_{race_data['race_id']}",
                        venue=venue,
                        race_number=race_data["race_number"],
                        start_time=datetime.fromtimestamp(race_data["start_time"]),
                        runners=self._parse_runners(race_data["runners"]),
                        source=self.source_name,
                    )
                    all_races.append(race)
                except (ValidationError, KeyError) as e:
                    log.error(
                        f"GreyhoundAdapter: Error parsing race {race_data.get('race_id', 'N/A')}",
                        error=str(e),
                        race_data=race_data,
                    )
        return all_races

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        """Parses a list of runner dictionaries into Runner objects."""
        runners = []
        for runner_data in runners_data:
            try:
                if runner_data.get("scratched", False):
                    continue

                odds_data = {}
                # The directive's example was flawed. Correcting to a more realistic structure.
                win_odds_val = runner_data.get("odds", {}).get("win")
                if win_odds_val is not None:
                    win_odds = Decimal(str(win_odds_val))
                    if win_odds > 1:
                        odds_data[self.source_name] = OddsData(
                            win=win_odds, source=self.source_name, last_updated=datetime.now()
                        )

                runner = Runner(
                    number=runner_data["trap_number"],
                    name=runner_data["dog_name"],
                    scratched=runner_data.get("scratched", False),
                    odds=odds_data,
                )
                runners.append(runner)
            except (KeyError, ValidationError) as e:
                log.error("GreyhoundAdapter: Error parsing runner", error=str(e), runner_data=runner_data)
        return runners
