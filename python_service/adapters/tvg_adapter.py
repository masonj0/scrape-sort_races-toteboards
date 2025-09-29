# python_service/adapters/tvg_adapter.py

import logging
from datetime import datetime
from typing import List, Optional, Dict

from .base import BaseAdapterV7, Race, Runner
from .utils import parse_odds

class TVGAdapter(BaseAdapterV7):
    """
    Adapter for the TVG mobile API.
    """
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def fetch_races(self) -> List[Race]:
        """
        Fetches race data from the TVG API and transforms it into the
        standardized Race model.
        """
        response_data = self.fetcher.get(self.BASE_URL)
        if not isinstance(response_data, dict) or 'races' not in response_data:
            logging.warning(f"TVGAdapter received invalid or non-dict data: {type(response_data)}")
            return []

        all_races = []
        for race_info in response_data.get('races', []):
            try:
                runners = []
                for r in race_info.get('runners', []):
                    if r.get('scratched'):
                        continue

                    # Extract the morning line odds string to pass to the centralized utility
                    morning_line_odds = r.get('odds', {}).get('morningLine')
                    if morning_line_odds is None:
                        continue

                    # Use the centralized utility to parse odds
                    odds_val = parse_odds(morning_line_odds)

                    # The utility returns 999.0 on failure; we should not include runners
                    # with unparseable odds, maintaining the original logic's intent.
                    if odds_val < 999.0:
                        runners.append(Runner(name=r.get('horseName', 'N/A'), odds=odds_val))

                if not runners:
                    continue

                post_time = datetime.fromisoformat(race_info['postTime'].replace('Z', '+00:00')) if race_info.get('postTime') else None

                all_races.append(
                    Race(
                        race_id=f"tvg_{race_info.get('raceId')}",
                        track_name=race_info.get('trackName', 'N/A'),
                        race_number=race_info.get('raceNumber'),
                        post_time=post_time,
                        runners=runners,
                        source=self.SOURCE_ID
                    )
                )
            except (KeyError, TypeError) as e:
                logging.warning(f"Skipping malformed TVG race due to missing key or type error: {e}")
                continue

        return all_races