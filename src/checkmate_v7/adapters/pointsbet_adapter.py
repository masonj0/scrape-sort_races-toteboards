#!/usr/bin/env python3
"""
A V3-compliant adapter for PointsBet's public racing API.
This is the second adapter of the V4 Polyglot Renaissance.
Logic translated from a Ruby open-source project.
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner

class PointsBetAdapter(BaseAdapterV7):
    """ An adapter for the PointsBet public API (AU). """

    SOURCE_ID = "pointsbet"
    API_URL = "https://api.au.pointsbet.com/api/v2/racing/races/today"

    def __init__(self, defensive_fetcher: DefensiveFetcher):
        super().__init__(defensive_fetcher)

    async def fetch_races(self) -> List[Race]:
        """ Fetches a list of races from the PointsBet API. """

        response = await self.fetcher.get(self.API_URL)
        if not response:
            return []

        return self._parse_races(response)

    def _parse_races(self, data: Dict[str, Any]) -> List[Race]:
        """ Parses the JSON response from the PointsBet API. """

        races: List[Race] = []

        for event in data.get("events", []):
            if not event.get("runners"):
                continue

            runners: List[Runner] = []
            for runner_data in event.get("runners", []):
                program_number = runner_data.get("runnerNumber")
                if not program_number:
                    continue

                odds = None
                if runner_data.get("fixedWinOdds"):
                    odds = runner_data["fixedWinOdds"].get("price")

                runners.append(
                    Runner(
                        name=runner_data.get("name"),
                        program_number=str(program_number),
                        odds=odds
                    )
                )

            if runners:
                race = Race(
                    race_id=event.get("key"),
                    track_name=event.get("meetingName"),
                    race_number=str(event.get("raceNumber")),
                    number_of_runners=len(runners),
                    runners=runners
                )
                races.append(race)

        return races
