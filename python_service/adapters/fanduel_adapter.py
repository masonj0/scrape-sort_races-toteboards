# python_service/adapters/fanduel_adapter.py

from datetime import datetime
from datetime import timedelta
from datetime import timezone
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

log = structlog.get_logger()


class FanDuelAdapter(BaseAdapter):
    """Adapter for fetching horse racing odds from FanDuel's private API."""

    source_name = "FanDuel"
    API_URL = "https://sb-api.nj.sportsbook.fanduel.com/api/markets?_ak=Fh2e68s832c41d4b&eventId="

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> List[Race]:
        """Fetches races for a given date. Note: FanDuel API is event-based, not date-based."""
        # This is a placeholder for a more robust event discovery mechanism.
        # For now, we'll use a known event ID for a major race day as a proof of concept.
        # A full implementation would need to first find the relevant event IDs for the day.
        event_id = "38183.3"  # Example: A major race event

        log.info("Fetching races from FanDuel", event_id=event_id)
        start_time = datetime.now()
        try:
            response = await http_client.get(self.API_URL + event_id)
            response.raise_for_status()
            data = response.json()
            races = self._parse_races(data)
            return self._format_response(races, start_time, is_success=True)
        except httpx.HTTPStatusError as e:
            log.error("FanDuel API request failed", status_code=e.response.status_code, response=e.response.text)
            return self._format_response([], start_time, is_success=False, error_message=str(e))
        except Exception as e:
            log.error("An unexpected error occurred fetching FanDuel data", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    def _parse_races(self, data: Dict[str, Any]) -> List[Race]:
        races = []
        if "marketGroups" not in data:
            log.warning("FanDuel response missing 'marketGroups' key")
            return []

        for group in data["marketGroups"]:
            if group.get("marketGroupName") == "Win":
                for market in group.get("markets", []):
                    try:
                        race = self._parse_single_race(market)
                        if race:
                            races.append(race)
                    except Exception as e:
                        log.error("Failed to parse a FanDuel market", market=market, error=str(e), exc_info=True)
        return races

    def _parse_single_race(self, market: Dict[str, Any]) -> Race | None:
        market_name = market.get("marketName", "")
        if not market_name.startswith("Race"):
            return None

        # Extract race number and track from market name (e.g., "Race 5 - Churchill Downs")
        parts = market_name.split(" - ")
        if len(parts) < 2:
            return None

        race_number_str = parts[0].replace("Race ", "")
        track_name = parts[1]

        # Placeholder for start_time - FanDuel's market API doesn't provide it directly
        start_time = datetime.now(timezone.utc) + timedelta(hours=int(race_number_str))

        runners = []
        for runner_data in market.get("runners", []):
            runner_name = runner_data.get("runnerName")
            win_odds = runner_data.get("winRunnerOdds", {}).get("currentPrice")
            if not runner_name or not win_odds:
                continue

            try:
                # Price is given as a fraction string, e.g., "12/5"
                numerator, denominator = map(int, win_odds.split("/"))
                decimal_odds = Decimal(numerator) / Decimal(denominator) + 1
            except (ValueError, ZeroDivisionError):
                log.warning("Could not parse FanDuel odds", odds_str=win_odds, runner=runner_name)
                continue

            odds = OddsData(win=decimal_odds, source=self.source_name, last_updated=datetime.now(timezone.utc))

            # Placeholder for program number
            program_number_str = runner_name.split(".")[0].strip()

            runner = Runner(
                name=runner_name.split(".")[1].strip(),
                number=int(program_number_str) if program_number_str.isdigit() else None,
                odds={self.source_name: odds},
            )
            runners.append(runner)

        if not runners:
            return None

        race_id = f"FD-{track_name.replace(' ', '')[:5].upper()}-{start_time.strftime('%Y%m%d')}-R{race_number_str}"

        return Race(
            id=race_id,
            venue=track_name,
            race_number=int(race_number_str),
            start_time=start_time,
            runners=runners,
            source=self.source_name,
        )
