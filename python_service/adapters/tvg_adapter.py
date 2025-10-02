# python_service/adapters/tvg_adapter.py

from .base import BaseAdapter
from ..models import RaceData, RunnerData
from typing import List
from datetime import datetime

class TVGAdapter(BaseAdapter):
    """Adapter for the TVG JSON API with improved headers."""
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def fetch_races(self) -> List[RaceData]:
        self.logger.info(f"Fetching races from {self.SOURCE_ID}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.tvg.com/'
        }
        response_data = self.fetcher.get(self.BASE_URL, headers=headers)
        if not response_data or 'races' not in response_data:
            return []

        races = []
        for item in response_data.get('races', []):
            try:
                runners = []
                for r in item.get('runners', []):
                    if not r.get('scratched'):
                        odds_val = r.get('odds', {}).get('decimal')
                        runners.append(RunnerData(name=r.get('horseName', 'Unknown'), odds=float(odds_val) if odds_val else None))

                races.append(RaceData(
                    race_id=f"tvg_{item['id']}",
                    track_name=item.get('trackName', 'Unknown Track'),
                    race_number=item.get('raceNumber', 0),
                    post_time=datetime.fromisoformat(item.get('postTime')),
                    runners=runners,
                    source=self.SOURCE_ID
                ))
            except Exception as e:
                self.logger.warning(f"Skipping malformed TVG race: {e}")
        return races