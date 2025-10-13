# python_service/adapters/tvg_adapter.py

import asyncio
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from decimal import Decimal, InvalidOperation

from .base import BaseAdapter
from ..models import Race, Runner, OddsData
from ..utils.odds import parse_odds_to_decimal

log = structlog.get_logger(__name__)

def _parse_program_number(program_str: str) -> int:
    """Safely parses program numbers like '1A' into an integer."""
    return int(''.join(filter(str.isdigit, program_str))) if program_str else 99

class TVGAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(
            source_name="TVG",
            base_url="https://api.tvg.com/v3/"
        )
        self.api_key = config.TVG_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        headers = {"Accept": "application/json", "X-API-Key": self.api_key}

        if not self.api_key:
            log.warning("TVGAdapter: TVG_API_KEY not set. Skipping.")
            return self._format_response([], start_time, is_success=False, error_message="ConfigurationError: TVG_API_KEY not set")

        try:
            tracks_url = "tracks"
            tracks_params = {"date": date, "country": "US"}
            tracks_response = await self.make_request(http_client, 'GET', tracks_url, headers=headers, params=tracks_params)

            if not tracks_response or 'tracks' not in tracks_response:
                log.warning("TVG: No tracks found for the given date.")
                return self._format_response([], start_time, is_success=True)

            # Create a list of tasks to fetch races for all tracks concurrently
            tasks = [self._fetch_races_for_track(track, date, http_client, headers) for track in tracks_response['tracks']]
            results_per_track = await asyncio.gather(*tasks, return_exceptions=True)

            # Flatten the list of lists into a single list of races
            all_races = []
            for result in results_per_track:
                if isinstance(result, list):
                    all_races.extend(result)
                elif isinstance(result, Exception):
                    log.error("TVGAdapter: A track fetch task failed", error=result)

            return self._format_response(all_races, start_time, is_success=True)
        except Exception as e:
            log.error("TVGAdapter: An unexpected error occurred", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=f"An unexpected error occurred: {e}")

    async def _fetch_races_for_track(self, track: Dict[str, Any], date: str, http_client: httpx.AsyncClient, headers: Dict) -> List[Race]:
        """Fetches all race details for a single track concurrently."""
        track_races = []
        track_code = track.get('code')
        if not track_code:
            return []

        try:
            races_url = f"tracks/{track_code}/races"
            races_params = {"date": date}
            races_response = await self.make_request(http_client, 'GET', races_url, headers=headers, params=races_params)
            if not races_response or 'races' not in races_response:
                return []

            # Create a list of tasks to fetch details for all races in this track concurrently
            detail_tasks = []
            for race_summary in races_response.get('races', []):
                race_detail_url = f"tracks/{track_code}/races/{race_summary['number']}"
                detail_tasks.append(self.make_request(http_client, 'GET', race_detail_url, headers=headers))

            race_details = await asyncio.gather(*detail_tasks, return_exceptions=True)

            for detail in race_details:
                if detail and not isinstance(detail, Exception):
                    parsed_race = self._parse_tvg_race(track, detail)
                    track_races.append(parsed_race)
            return track_races
        except Exception as e:
            log.error("TVGAdapter: Failed to process track", track_name=track.get('name'), error=str(e))
            return [] # Return empty list for this track on failure

    def _parse_tvg_race(self, track: Dict[str, Any], race_data: Dict[str, Any]) -> Race:
        runners = []
        for runner_data in race_data.get('runners', []):
            if not runner_data.get('scratched'):
                current_odds_str = runner_data.get('odds', {}).get('current') or runner_data.get('odds', {}).get('morningLine')
                win_odds = parse_odds_to_decimal(current_odds_str)
                odds_dict = {}
                if win_odds and win_odds < 999:
                    odds_dict[self.source_name] = OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())
                runners.append(Runner(number=_parse_program_number(runner_data.get('programNumber')), name=runner_data.get('horseName', 'Unknown Runner'), scratched=False, odds=odds_dict))
        race_id = f"{track.get('code', 'UNK').lower()}_{race_data['postTime'].split('T')[0]}_R{race_data['number']}"
        return Race(id=race_id, venue=track.get('name', 'Unknown Venue'), race_number=race_data.get('number'), start_time=datetime.fromisoformat(race_data.get('postTime')), runners=runners, source=self.source_name)