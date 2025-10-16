# python_service/adapters/theracingapi_adapter.py

from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List

import httpx
import structlog

from ..models import OddsData
from ..models import Race
from ..models import Runner
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class TheRacingApiAdapter(BaseAdapter):
    """Adapter for the high-value JSON-based The Racing API."""

    def __init__(self, config):
        super().__init__(source_name="TheRacingAPI", base_url="https://api.theracingapi.com/v1/", config=config)
        self.api_key = config.THE_RACING_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        if not self.api_key:
            return self._format_response(
                [], start_time, is_success=False, error_message="ConfigurationError: THE_RACING_API_KEY not set"
            )

        try:
            endpoint = f"racecards?date={date}&course=all&region=gb,ire"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self.make_request(http_client, "GET", endpoint, headers=headers)

            if not response:
                return self._format_response(
                    [], start_time, is_success=True, error_message="No response from API."
                )

            response_json = response.json()
            if not response_json or not response_json.get("racecards"):
                return self._format_response(
                    [], start_time, is_success=True, error_message="No racecards found in API response."
                )

            all_races = self._parse_races(response_json["racecards"])
            return self._format_response(all_races, start_time, is_success=True)
        except httpx.HTTPError as e:
            log.error(f"{self.source_name}: HTTP request failed after retries", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message="API request failed after multiple retries."
            )
        except Exception as e:
            log.error(f"{self.source_name}: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response(
                [], start_time, is_success=False, error_message=f"An unexpected error occurred: {e}"
            )

    def _parse_races(self, racecards: List[Dict[str, Any]]) -> List[Race]:
        races = []
        for race_data in racecards:
            try:
                start_time = datetime.fromisoformat(race_data["off_time"].replace("Z", "+00:00"))

                race = Race(
                    id=f"tra_{race_data['race_id']}",
                    venue=race_data["course"],
                    race_number=race_data["race_no"],
                    start_time=start_time,
                    runners=self._parse_runners(race_data.get("runners", [])),
                    source=self.source_name,
                    race_name=race_data.get("race_name"),
                    distance=race_data.get("distance_f"),
                )
                races.append(race)
            except Exception as e:
                log.error(f"{self.source_name}: Error parsing race", race_id=race_data.get("race_id"), error=str(e))
        return races

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        runners = []
        for i, runner_data in enumerate(runners_data):
            try:
                odds_data = {}
                if runner_data.get("odds"):
                    win_odds = Decimal(str(runner_data["odds"][0]["odds_decimal"]))
                    odds_data[self.source_name] = OddsData(
                        win=win_odds, source=self.source_name, last_updated=datetime.now()
                    )

                runners.append(
                    Runner(
                        number=runner_data.get("number", i + 1),
                        name=runner_data["horse"],
                        odds=odds_data,
                        jockey=runner_data.get("jockey"),
                        trainer=runner_data.get("trainer"),
                    )
                )
            except Exception as e:
                log.error(
                    f"{self.source_name}: Error parsing runner", runner_name=runner_data.get("horse"), error=str(e)
                )
        return runners

    def _format_response(
        self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None
    ) -> Dict[str, Any]:
        return {
            "races": races,
            "source_info": {
                "name": self.source_name,
                "status": "SUCCESS" if is_success else "FAILED",
                "races_fetched": len(races),
                "error_message": error_message,
                "fetch_duration": (datetime.now() - start_time).total_seconds(),
            },
        }
