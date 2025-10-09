# python_service/adapters/gbgb_api_adapter.py

import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from decimal import Decimal

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

log = structlog.get_logger(__name__)

class GbgbApiAdapter(BaseAdapter):
    """Adapter for the undocumented JSON API for the Greyhound Board of Great Britain."""

    def __init__(self, config):
        super().__init__(
            source_name="GBGB",
            base_url="https://api.gbgb.org.uk/api/"
        )

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            # The endpoint appears to be structured by date for all meetings
            endpoint = f"results/meeting/{date}"
            response_json = await self.make_request(http_client, 'GET', endpoint)

            if not response_json:
                return self._format_response([], start_time, is_success=True, error_message="No meetings found in API response.")

            all_races = self._parse_meetings(response_json)
            return self._format_response(all_races, start_time, is_success=True)
        except httpx.HTTPError as e:
            log.error(f"{self.source_name}: HTTP request failed after retries", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message="API request failed after multiple retries.")
        except Exception as e:
            log.error(f"{self.source_name}: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=f"An unexpected error occurred: {e}")

    def _parse_meetings(self, meetings_data: List[Dict[str, Any]]) -> List[Race]:
        races = []
        for meeting in meetings_data:
            track_name = meeting.get('trackName')
            for race_data in meeting.get('races', []):
                try:
                    races.append(self._parse_race(race_data, track_name))
                except Exception as e:
                    log.error(f"{self.source_name}: Error parsing race", race_id=race_data.get('raceId'), error=str(e))
        return races

    def _parse_race(self, race_data: Dict[str, Any], track_name: str) -> Race:
        return Race(
            id=f"gbgb_{race_data['raceId']}",
            venue=track_name,
            race_number=race_data['raceNumber'],
            start_time=datetime.fromisoformat(race_data['raceTime'].replace('Z', '+00:00')),
            runners=self._parse_runners(race_data.get('traps', [])),
            source=self.source_name,
            race_name=race_data.get('raceTitle'),
            distance=f"{race_data.get('raceDistance')}m",
        )

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        runners = []
        for runner_data in runners_data:
            try:
                # The API provides SP as a fraction, e.g., '5/2'
                odds_data = {}
                sp = runner_data.get('sp')
                if sp:
                    from .utils import parse_odds # Local import to avoid circular dependency issues at module level
                    win_odds = Decimal(str(parse_odds(sp)))
                    if win_odds < 999:
                        odds_data[self.source_name] = OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())

                runners.append(Runner(
                    number=runner_data['trapNumber'],
                    name=runner_data['dogName'],
                    odds=odds_data,
                ))
            except Exception as e:
                log.error(f"{self.source_name}: Error parsing runner", runner_name=runner_data.get('dogName'), error=str(e))
        return runners

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': (datetime.now() - start_time).total_seconds()
            }
        }