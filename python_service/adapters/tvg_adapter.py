# python_service/adapters/tvg_adapter.py

import logging
from datetime import datetime
from typing import Dict, Any

import aiohttp

from ..models import RaceData, RunnerData
from .base import BaseAdapter

class TVGAdapter(BaseAdapter):
    """
    An adapter for fetching race data from the TVG API.
    """
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    async def fetch_races(self) -> Dict[str, Any]:
        """
        Asynchronously fetches race data from the TVG API.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json', 'Referer': 'https://www.tvg.com/'
        }

        try:
            session = await self.get_session()
            async with session.get(self.BASE_URL, headers=headers, timeout=15) as response:
                response.raise_for_status()
                response_data = await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching TVG data: {e}")
            return {"races": [], "error": f"AIOHTTP Error: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred fetching TVG data: {e}")
            return {"races": [], "error": f"Unexpected Error: {e}"}

        if not isinstance(response_data, dict) or 'races' not in response_data:
            return {"races": [], "error": "InvalidResponse: API response did not contain a 'races' key"}

        races = []
        for item in response_data.get('races', []):
            try:
                runners = []
                for r_data in item.get('runners', []):
                    if not r_data.get('scratched'):
                        odds_val = r_data.get('odds', {}).get('decimal')
                        runners.append(RunnerData(name=r_data.get('horseName', 'Unknown'), odds=float(odds_val) if odds_val else None))
                if not runners:
                    continue

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

        return {"races": races}