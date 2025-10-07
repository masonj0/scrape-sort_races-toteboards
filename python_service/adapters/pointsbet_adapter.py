# python_service/adapters/pointsbet_adapter.py

import structlog
from datetime import datetime
from typing import Dict, Any, List
import httpx
from decimal import Decimal

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

log = structlog.get_logger(__name__)

class PointsBetAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(
            source_name="PointsBet",
            base_url="https://api.au.pointsbet.com"
        )
        self.api_key = config.POINTSBET_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Fetches upcoming thoroughbred races from the PointsBet API."""
        start_time = datetime.now()

        if not self.api_key:
            log.warning("PointsBetAdapter: POINTSBET_API_KEY not set. Skipping.")
            return self._format_response([], start_time, is_success=False, error_message="ConfigurationError: Token not set")

        endpoint = "/api/v2/racing/futures"
        headers = {"api-key": self.api_key}
        params = {"sportId": 21}  # Assuming 21 is for Thoroughbred Racing

        try:
            response_json = await self.make_request(http_client, 'GET', endpoint, headers=headers, params=params)

            if "events" not in response_json:
                log.warning("PointsBetAdapter: No 'events' in response or empty response.")
                return self._format_response([], start_time)

            all_races = self._parse_races(response_json["events"])

            # The API is for futures, so we must filter by the requested date
            all_races = [race for race in all_races if race.start_time.strftime('%Y-%m-%d') == date]

            return self._format_response(all_races, start_time)
        except httpx.HTTPError as e: # Catching specific HTTP errors from tenacity retries
            log.error("PointsBetAdapter: HTTP request failed after retries", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message="API request failed after multiple retries.")
        except Exception as e: # Catch-all for other unexpected errors
            log.error("PointsBetAdapter: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=f"An unexpected error occurred: {e}")

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
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

    def _parse_races(self, events: List[Dict[str, Any]]) -> List[Race]:
        races = []
        for event in events:
            if not event.get("outcomes"):  # Skip events without runners
                continue

            try:
                race = Race(
                    id=f"pb_{event['id']}",
                    venue=event.get("competitionName", "Unknown Venue"),
                    race_number=event.get("eventNumber", 0),
                    start_time=datetime.fromisoformat(event["startTime"].replace("Z", "+00:00")),
                    runners=self._parse_runners(event["outcomes"]),
                    source=self.source_name
                )
                races.append(race)
            except Exception as e:
                log.error(
                    "PointsBetAdapter: Error parsing event",
                    error=str(e),
                    event_id=event.get('id', 'N/A')
                )
        return races

    def _parse_runners(self, outcomes: List[Dict[str, Any]]) -> List[Runner]:
        runners = []
        for i, outcome in enumerate(outcomes):
            win_odds_data = next((p for p in outcome.get("prices", []) if p["priceType"] == "FixedWin"), None)

            odds_dict = {}
            if win_odds_data and win_odds_data.get("price"):
                try:
                    win_odds = Decimal(str(win_odds_data["price"]))
                    odds_dict[self.source_name] = OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())
                except Exception:
                    win_odds = None

            runners.append(Runner(
                number=i + 1,  # Placeholder as number is not provided
                name=outcome.get("name", "Unknown Runner"),
                scratched=outcome.get("isSuspended", False),
                odds=odds_dict
            ))
        return runners
