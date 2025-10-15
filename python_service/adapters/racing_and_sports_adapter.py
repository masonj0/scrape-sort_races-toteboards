# python_service/adapters/racing_and_sports_adapter.py

from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

import httpx
import structlog

from ..models import Race
from ..models import Runner
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class RacingAndSportsAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(source_name="Racing and Sports", base_url="https://api.racingandsports.com.au/")
        self.api_token = config.RACING_AND_SPORTS_TOKEN

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        all_races: List[Race] = []
        headers = {"Authorization": f"Bearer {self.api_token}", "Accept": "application/json"}

        if not self.api_token:
            return self._format_response(
                [], start_time, is_success=False, error_message="ConfigurationError: Token not set"
            )

        try:
            meetings_url = "v1/racing/meetings"
            params = {"date": date, "jurisdiction": "AUS"}
            meetings_data = await self.make_request(http_client, "GET", meetings_url, headers=headers, params=params)

            if not meetings_data or not meetings_data.get("meetings"):
                return self._format_response(all_races, start_time, is_success=True)

            for meeting in meetings_data["meetings"]:
                for race_summary in meeting.get("races", []):
                    try:
                        parsed_race = self._parse_ras_race(meeting, race_summary)
                        all_races.append(parsed_race)
                    except Exception as e:
                        log.error(
                            "RacingAndSportsAdapter: Failed to parse race",
                            meeting=meeting.get("venueName"),
                            error=str(e),
                            exc_info=True,
                        )

            return self._format_response(all_races, start_time, is_success=True)
        except httpx.HTTPError as e:
            log.error("RacingAndSportsAdapter: HTTP request failed after retries", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message="API request failed after multiple retries."
            )
        except Exception as e:
            log.error("RacingAndSportsAdapter: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message=f"An unexpected error occurred: {e}"
            )

    def _format_response(
        self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None
    ) -> Dict[str, Any]:
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

    def _parse_ras_race(self, meeting: Dict[str, Any], race: Dict[str, Any]) -> Race:
        runners = [
            Runner(
                number=rd.get("runnerNumber"),
                name=rd.get("horseName", "Unknown"),
                scratched=rd.get("isScratched", False),
            )
            for rd in race.get("runners", [])
        ]

        return Race(
            id=f"ras_{race.get('raceId')}",
            venue=meeting.get("venueName", "Unknown Venue"),
            race_number=race.get("raceNumber"),
            start_time=datetime.fromisoformat(race.get("startTime")),
            runners=runners,
            source=self.source_name,
        )
