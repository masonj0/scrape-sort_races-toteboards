# python_service/adapters/tvg_adapter.py

import logging
from datetime import datetime
from ..models import RaceData, RunnerData
from .base import BaseAdapter

class TVGAdapter(BaseAdapter):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def fetch_races(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json', 'Referer': 'https://www.tvg.com/'
        }
        fetch_result = self.fetcher.get(self.BASE_URL, headers=headers, source_id=self.SOURCE_ID)

        if not fetch_result['success']:
            return {'success': False, 'error_details': fetch_result}

        response_data = fetch_result['data']
        if not isinstance(response_data, dict) or 'races' not in response_data:
            return {'success': False, 'error_details': {'error': 'InvalidResponse', 'message': 'API response did not contain a races key'}}

        races = []
        for item in response_data.get('races', []):
            try:
                runners = []
                for r_data in item.get('runners', []):
                    if not r_data.get('scratched'):
                        odds_val = r_data.get('odds', {}).get('decimal')
                        runners.append(RunnerData(name=r_data.get('horseName', 'Unknown'), odds=float(odds_val) if odds_val else None))
                if not runners: continue

                races.append(RaceData(
                    race_id=f"tvg_{item['id']}", track_name=item.get('trackName', 'Unknown Track'),
                    race_number=item.get('raceNumber', 0), post_time=datetime.fromisoformat(item.get('postTime')),
                    runners=runners, source=self.SOURCE_ID
                ))
            except Exception as e:
                self.logger.warning(f"Skipping malformed TVG race: {e}")

        return {'success': True, 'data': races}