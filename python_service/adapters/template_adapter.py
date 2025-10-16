#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
#  Fortuna Faucet: Canonical Adapter Template
# ==============================================================================
# This file is the official template for creating new adapters. It is based on
# the clean and simple design of the RacingAndSportsAdapter.
# ==============================================================================

from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

import httpx
import structlog

from ..models import Race  # Assuming standard models
from ..models import Runner  # Assuming standard models
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class TemplateAdapter(BaseAdapter):
    """[IMPLEMENT ME] A brief description of the data source."""

    def __init__(self, config):
        super().__init__(source_name="[IMPLEMENT ME] Example Source", base_url="https://api.example.com")
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
