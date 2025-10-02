# python_service/adapters/tvg_adapter.py

import logging
from datetime import datetime
import aiohttp

from ..models import Race, Runner
from .base import BaseAdapter

class TVGAdapter(BaseAdapter):
    """
    An adapter for fetching race data from the TVG API.
    """
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    async def fetch_races(self):
        """
        Asynchronously fetches and processes race data from the TVG API.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json', 'Referer': 'https://www.tvg.com/'
        }

        try:
            session = await self.get_session()
            async with session.get(self.BASE_URL, headers=headers) as response:
                response.raise_for_status()
                response_data = await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching TVG data: {e}")
            return {'success': False, 'error_details': {'error': 'NetworkError', 'message': str(e)}}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred fetching TVG data: {e}")
            return {'success': False, 'error_details': {'error': 'UnexpectedError', 'message': str(e)}}

        if not isinstance(response_data, dict) or 'races' not in response_data:
            return {'success': False, 'error_details': {'error': 'InvalidResponse', 'message': 'API response did not contain a races key'}}

        races = []
        for item in response_data.get('races', []):
            try:
                runners = []
                for r_data in item.get('runners', []):
                    if not r_data.get('scratched'):
                        odds_val = r_data.get('odds', {}).get('decimal')
                        runners.append(Runner(name=r_data.get('horseName', 'Unknown'), odds=float(odds_val) if odds_val else None))
                if not runners: continue

                races.append(Race(
                    id=f"tvg_{item['id']}",
                    venue=item.get('trackName', 'Unknown Track'),
                    race_number=item.get('raceNumber', 0),
                    race_time=datetime.fromisoformat(item.get('postTime')),
                    runners=runners,
                    source=self.SOURCE_ID
                ))
            except Exception as e:
                self.logger.warning(f"Skipping malformed TVG race: {e}")

        return {'success': True, 'data': races}