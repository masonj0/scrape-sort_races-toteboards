# python_service/adapters/tvg_adapter.py
from datetime import datetime
from typing import Any, List, Optional

from ..models import Race, Runner
from ..utils.text import clean_text
from .base_v3 import BaseAdapterV3

class TVGAdapter(BaseAdapterV3):
    """Adapter for fetching US racing data from the TVG API, using BaseAdapterV3."""

    SOURCE_NAME = "TVG"
    BASE_URL = "https://api.tvg.com/v2/races/"

    def __init__(self, config=None):
        super().__init__(source_name=self.SOURCE_NAME, base_url=self.BASE_URL)
        self.config = config or {}
        self.tvg_api_key = self.config.TVG_API_KEY
        if not self.tvg_api_key:
            self.logger.warning("TVG_API_KEY is not set. Adapter will be non-functional.")

    async def _fetch_data(self, date: str) -> Any:
        """Fetches all race details for a given date by first getting tracks."""
        if not self.tvg_api_key:
            return None

        headers = {"X-Api-Key": self.tvg_api_key}
        tracks_response = await self.http_client.get(f"{self.BASE_URL}summary?date={date}&country=USA", headers=headers)
        tracks_response.raise_for_status()
        tracks_data = tracks_response.json()

        all_race_details = []
        for track in tracks_data.get('tracks', []):
            track_id = track.get('id')
            for race in track.get('races', []):
                race_id = race.get('id')
                if track_id and race_id:
                    details_response = await self.http_client.get(f"{self.BASE_URL}{track_id}/{race_id}", headers=headers)
                    if details_response.status_code == 200:
                        all_race_details.append(details_response.json())
        return all_race_details

    def _parse_races(self, raw_data: Any) -> List[Race]:
        """Parses the list of detailed race JSON objects into Race models."""
        races = []
        for race_detail in raw_data:
            try:
                track = race_detail.get('track', {})
                race_info = race_detail.get('race', {})

                runners = []
                for runner_data in race_detail.get('runners', []):
                    if runner_data.get('scratched'):
                        continue

                    odds = runner_data.get('odds', {})
                    current_odds = odds.get('currentPrice', {})
                    odds_str = current_odds.get('fractional') or odds.get('morningLinePrice', {}).get('fractional')

                    runners.append(Runner(
                        number=int(runner_data.get('programNumber', '0').replace('A', '')),
                        name=clean_text(runner_data.get('name')),
                        odds=odds_str,
                        scratched=False
                    ))

                if runners:
                    race = Race(
                        id=f"tvg_{track.get('code', 'UNK')}_{race_info.get('date', 'NODATE')}_{race_info.get('number', 0)}",
                        venue=track.get('name'),
                        race_number=race_info.get('number'),
                        start_time=datetime.fromisoformat(race_info.get('postTime').replace('Z', '+00:00')),
                        runners=runners,
                        source=self.SOURCE_NAME
                    )
                    races.append(race)
            except (ValueError, AttributeError):
                self.logger.warning("Failed to parse a TVG race detail.", exc_info=True)
                continue
        return races

    async def fetch_races(self, date: str, http_client):
        pass
