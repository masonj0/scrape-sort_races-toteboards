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

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..fetcher import get_page_content

class PointsBetAdapter(BaseAdapterV3):
    """ An adapter for the PointsBet public API (AU). """

    SOURCE_ID = "pointsbet"
    API_URL = "https://api.au.pointsbet.com/api/v2/racing/races/today"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def fetch(self) -> List[NormalizedRace]:
        """ Fetches today's racing events from the PointsBet AU API. """
        text_content = await get_page_content(self.API_URL)
        if not text_content:
            return []

        try:
            json_content = json.loads(text_content)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from PointsBet API.")
            return []

        if 'events' not in json_content:
            return []

        return self.parse(json_content.get('events', []))

    def parse(self, events: List[Dict[str, Any]]) -> List[NormalizedRace]:
        """ Parses the JSON response from the PointsBet API. """
        all_races = []
        for event in events:
            try:
                # We only want to process events that are actual races with runners
                if not event.get('runners') or not event.get('meetingName'):
                    continue

                runners = []
                for runner in event.get('runners', []):
                    # PointsBet provides fixed odds for win, which is what we need
                    odds = runner.get('fixedWinOdds', {}).get('price')
                    program_number = runner.get('runnerNumber')
                    if odds and program_number:
                        runners.append(NormalizedRunner(
                            name=runner.get('name'),
                            odds=float(odds),
                            program_number=int(program_number)
                        ))

                if runners:
                    race_id = event.get('key')
                    track_name = event.get('meetingName')
                    if not race_id:
                        # Fallback if key is not present
                        race_number = event.get('raceNumber')
                        race_id = f"{track_name.replace(' ', '')}-{race_number}"

                    all_races.append(NormalizedRace(
                        race_id=race_id,
                        track_name=track_name,
                        race_number=event.get('raceNumber'),
                        post_time=datetime.fromisoformat(event.get('startTime')),
                        number_of_runners=len(runners),
                        runners=runners
                    ))
            except (KeyError, TypeError, ValueError) as e:
                # This prevents a single malformed event from crashing the whole process
                logging.warning(f"Skipping a malformed event in PointsBet parse: {e}")
                continue
        return all_races

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """Not used for API-based adapters, but required by BaseAdapterV3."""
        return []
