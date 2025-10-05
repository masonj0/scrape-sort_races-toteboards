from datetime import datetime
from typing import Any, Dict, List
import httpx
from pydantic import ValidationError, Field
import structlog
from decimal import Decimal

from ..models import Race, Runner, OddsData
from .base import BaseAdapter

log = structlog.get_logger(__name__)

class HarnessAdapter(BaseAdapter):
    """Adapter for fetching Harness racing data from USTA."""

    def __init__(self, config):
        super().__init__(
            source_name="Harness Racing (USTA)",
            base_url="https://data.ustrotting.com/"
        )
        # No API key required for this public endpoint

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Fetches upcoming harness races for the specified date."""
        start_time = datetime.now()
        endpoint = f"api/racenet/racing/card/{date}"
        try:
            response_json = await self.make_request(http_client, 'GET', endpoint)
            if not response_json or "meetings" not in response_json:
                log.warning("HarnessAdapter: No 'meetings' in response or empty response.")
                return self._format_response([], start_time, is_success=True, error_message="No meetings found for date.")

            all_races = self._parse_meetings(response_json["meetings"])
            return self._format_response(all_races, start_time)
        except httpx.HTTPStatusError as e:
            log.error("HarnessAdapter: HTTP error while fetching races", error=e, response_text=e.response.text)
            return self._format_response([], start_time, is_success=False, error_message=f"HTTP Error: {e.response.status_code}")
        except Exception as e:
            log.error("HarnessAdapter: An unexpected error occurred", error=e, exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=f"An unexpected error occurred: {str(e)}")

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        """Formats the adapter's response consistently."""
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }

    def _parse_meetings(self, meetings: List[Dict[str, Any]]) -> List[Race]:
        """Parses a list of meetings and their races into Race objects."""
        all_races = []
        for meeting in meetings:
            venue = meeting.get("trackName", "Unknown Venue")
            races_data = meeting.get("races", [])
            for race_data in races_data:
                try:
                    if not race_data.get("runners"):
                        continue

                    race = Race(
                        id=f"usta_{race_data['raceId']}", # Correct field: id
                        venue=venue,
                        race_number=race_data["raceNumber"],
                        start_time=datetime.fromisoformat(race_data["startTime"].replace("Z", "+00:00")),
                        runners=self._parse_runners(race_data["runners"]),
                        source=self.source_name
                    )
                    all_races.append(race)
                except (ValidationError, KeyError) as e:
                    log.error(
                        f"HarnessAdapter: Error parsing race {race_data.get('raceId', 'N/A')}",
                        error=str(e),
                        race_data=race_data
                    )
        return all_races

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        """Parses a list of runner dictionaries into Runner objects."""
        runners = []
        for runner_data in runners_data:
            try:
                # API provides number as 'postPosition'
                runner_number = runner_data.get('postPosition')
                if not runner_number:
                    continue

                # Adapt to the Runner model's odds structure
                odds_data = {}
                win_odds_str = runner_data.get("morningLineOdds") # Assuming M/L odds are the target
                if win_odds_str:
                    try:
                        # Handle fractional odds like "5/2" or simple odds like "5"
                        if '/' in win_odds_str:
                            numerator, denominator = map(int, win_odds_str.split('/'))
                            decimal_odds = Decimal(numerator) / Decimal(denominator) + 1
                        else:
                            decimal_odds = Decimal(win_odds_str) + 1

                        if decimal_odds > 1:
                            odds_data[self.source_name] = OddsData(
                                win=decimal_odds,
                                source=self.source_name,
                                last_updated=datetime.now()
                            )
                    except (ValueError, TypeError):
                         log.warning("Could not parse odds", odds_str=win_odds_str)


                runner = Runner(
                    number=runner_number,
                    name=runner_data["horseName"],
                    scratched=runner_data.get("scratched", False),
                    odds=odds_data
                )
                runners.append(runner)
            except (KeyError, ValidationError) as e:
                log.error("HarnessAdapter: Error parsing runner", error=str(e), runner_data=runner_data)
        return runners
