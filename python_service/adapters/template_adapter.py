#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
#  Fortuna Faucet: Canonical Adapter Template
# ==============================================================================
# This file is the official template for creating new adapters. It is based on
# the clean and simple design of the RacingAndSportsAdapter.
# ==============================================================================

from datetime import datetime
from typing import Dict, Any, List
import httpx
import structlog

from .base import BaseAdapter
from ..models import Race, Runner # Assuming standard models

log = structlog.get_logger(__name__)

class TemplateAdapter(BaseAdapter):
    """[IMPLEMENT ME] A brief description of the data source."""

    def __init__(self, config):
        super().__init__(
            source_name="[IMPLEMENT ME] Example Source",
            base_url="https://api.example.com"
        )
        # self.api_key = config.EXAMPLE_API_KEY # Uncomment if needed

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """[IMPLEMENT ME] The core logic for fetching and parsing races."""
        start_time = datetime.now()
        all_races: List[Race] = []

        # --- Example Logic ---
        # endpoint = f"/v1/races/{date}"
        # headers = {"X-Api-Key": self.api_key}
        # response_json = await self.make_request(http_client, 'GET', endpoint, headers=headers)
        # if not response_json or 'data' not in response_json:
        #     return self._format_response(all_races, start_time)
        #
        # for race_data in response_json['data']:
        #     parsed_race = self._parse_race(race_data)
        #     all_races.append(parsed_race)
        # --- End Example ---

        log.warning("TemplateAdapter.fetch_races is a stub and is not implemented.")
        return self._format_response(all_races, start_time)

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        """Formats the adapter's response consistently."""
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': [r.model_dump() for r in races],
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }

    def _parse_race(self, race_data: Dict[str, Any]) -> Race:
        """[IMPLEMENT ME] Logic to parse a single race from the source's data structure."""
        # Example:
        # runners = self._parse_runners(race_data.get('runners', []))
        # return Race(
        #     id=f"template_{race_data['id']}",
        #     venue=race_data['venue_name'],
        #     race_number=race_data['race_number'],
        #     start_time=datetime.fromisoformat(race_data['start_time']),
        #     runners=runners,
        #     source=self.source_name
        # )
        raise NotImplementedError("'_parse_race' is not implemented in TemplateAdapter.")

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        """[IMPLEMENT ME] Logic to parse a list of runners."""
        raise NotImplementedError("'_parse_runners' is not implemented in TemplateAdapter.")