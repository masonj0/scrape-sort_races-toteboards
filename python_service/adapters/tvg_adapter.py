# python_service/adapters/tvg_adapter.py

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from decimal import Decimal, InvalidOperation

from .base import BaseAdapter
from ..models import Race, Runner, OddsData

class TVGAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(
            source_name="TVG",
            base_url="https://api.tvg.com/v3/"
        )
        self.api_key = config.TVG_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        all_races: List[Race] = []
        headers = {"Accept": "application/json", "X-API-Key": self.api_key}

        if not self.api_key:
            self.logger.warning(f"TVG_API_KEY not set. Adapter {self.source_name} will be skipped.")
            return self._format_response(all_races, start_time)

        try:
            tracks_url = "tracks"
            tracks_params = {"date": date, "country": "US"}
            tracks_response = await self.make_request(http_client, 'GET', tracks_url, headers=headers, params=tracks_params)

            if not tracks_response or 'tracks' not in tracks_response:
                self.logger.warning("TVG: No tracks found for the given date.")
                return self._format_response(all_races, start_time)

            for track in tracks_response['tracks']:
                try:
                    races_url = f"tracks/{track['code']}/races"
                    races_params = {"date": date}
                    races_response = await self.make_request(http_client, 'GET', races_url, headers=headers, params=races_params)

                    for race_summary in races_response.get('races', []):
                        race_detail_url = f"tracks/{track['code']}/races/{race_summary['number']}"
                        race_detail = await self.make_request(http_client, 'GET', race_detail_url, headers=headers)
                        if race_detail:
                            parsed_race = self._parse_tvg_race(track, race_detail)
                            all_races.append(parsed_race)
                except Exception as e:
                    self.logger.error(f"Failed to process track {track.get('name')}: {e}", exc_info=True)

            return self._format_response(all_races, start_time)
        except Exception as e:
            self.logger.error(f"Failed to fetch races from {self.source_name}: {e}", exc_info=True)
            raise

    def _format_response(self, races: List[Race], start_time: datetime) -> Dict[str, Any]:
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': races,
            'source_info': {
                'name': self.source_name, 'status': 'SUCCESS',
                'races_fetched': len(races), 'error_message': None,
                'fetch_duration': fetch_duration
            }
        }

    def _parse_tvg_race(self, track: Dict[str, Any], race_data: Dict[str, Any]) -> Race:
        runners = []
        for runner_data in race_data.get('runners', []):
            if not runner_data.get('scratched'):
                current_odds_str = runner_data.get('odds', {}).get('current') or runner_data.get('odds', {}).get('morningLine')
                win_odds = self._parse_tvg_odds(current_odds_str)

                odds_dict = {}
                if win_odds:
                    odds_dict[self.source_name] = OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())

                runners.append(Runner(
                    number=runner_data.get('programNumber'),
                    name=runner_data.get('horseName', 'Unknown Runner'),
                    scratched=False, # Corrected based on Oracle feedback
                    odds=odds_dict
                ))

        race_id = f"{track.get('code', 'UNK').lower()}_{race_data['postTime'].split('T')[0]}_R{race_data['number']}"

        return Race(
            id=race_id,
            venue=track.get('name', 'Unknown Venue'),
            race_number=race_data.get('number'),
            start_time=datetime.fromisoformat(race_data.get('postTime')),
            runners=runners,
            source=self.source_name # Corrected based on Oracle feedback
        )

    def _parse_tvg_odds(self, odds_string: str) -> Optional[Decimal]:
        # Corrected based on Oracle feedback to return Decimal
        if not odds_string or odds_string == "SCR": return None
        if odds_string == "EVEN": return Decimal('2.0')
        if "/" in odds_string:
            try:
                numerator, denominator = odds_string.split("/")
                return (Decimal(numerator) / Decimal(denominator)) + Decimal('1.0')
            except (ValueError, ZeroDivisionError, InvalidOperation): return None
        try: return Decimal(odds_string)
        except InvalidOperation: return None