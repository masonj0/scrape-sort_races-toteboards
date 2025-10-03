# python_service/adapters/racing_and_sports_adapter.py

import os
from datetime import datetime
from typing import Dict, Any, List
import httpx

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

class RacingAndSportsAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(
            source_name="Racing and Sports",
            base_url="https://api.racingandsports.com.au/"
        )
        self.api_token = os.getenv("RACING_AND_SPORTS_TOKEN")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        all_races: List[Race] = []
        headers = {"Authorization": f"Bearer {self.api_token}", "Accept": "application/json"}

        if not self.api_token:
            self.logger.warning(f"{self.source_name}: RACING_AND_SPORTS_TOKEN not set. Skipping.")
            return self._format_response(all_races, start_time, is_success=False, error_message="ConfigurationError: Token not set")

        try:
            meetings_url = "v1/racing/meetings"
            params = {"date": date, "jurisdiction": "AUS"}
            meetings_data = await self.make_request(http_client, 'GET', meetings_url, headers=headers, params=params)

            if not meetings_data or not meetings_data.get('meetings'):
                return self._format_response(all_races, start_time)

            for meeting in meetings_data['meetings']:
                for race_summary in meeting.get('races', []):
                    try:
                        # A full implementation would fetch each race's runners, but we'll parse the summary
                        parsed_race = self._parse_ras_race(meeting, race_summary)
                        all_races.append(parsed_race)
                    except Exception as e:
                        self.logger.error(f"Failed to parse race for meeting {meeting.get('venueName')}: {e}", exc_info=True)

            return self._format_response(all_races, start_time)
        except Exception as e:
            self.logger.error(f"Failed to fetch races from {self.source_name}: {e}", exc_info=True)
            raise

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': [r.model_dump() for r in races],
            'source_info': {
                'name': self.source_name, 'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races), 'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }

    def _parse_ras_race(self, meeting: Dict[str, Any], race: Dict[str, Any]) -> Race:
        runners = []
        for runner_data in race.get('runners', []):
            runners.append(Runner(
                number=runner_data.get('runnerNumber'),
                name=runner_data.get('horseName', 'Unknown Runner'),
                scratched=runner_data.get('isScratched', False)
            ))

        return Race(
            id=f"ras_{race.get('raceId')}",
            venue=meeting.get('venueName', 'Unknown Venue'),
            race_number=race.get('raceNumber'),
            start_time=datetime.fromisoformat(race.get('startTime')),
            runners=runners,
            source=self.source_name
        )