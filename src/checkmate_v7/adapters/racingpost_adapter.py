"""
The new, modern Racing Post adapter.
"""
from typing import List, Optional
from datetime import datetime
import logging
import json
import re

from bs4 import BeautifulSoup

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner


class RacingPostModernAdapter(BaseAdapterV7):
    """
    Adapter for the Racing Post website.
    This is the modern implementation, refactored into its own module.
    """
    SOURCE_ID = "racingpost"
    BASE_URL = "https://www.racingpost.com"

    def fetch_races(self) -> List[Race]:
        """
        Fetches and parses races from the main Racing Post racecards page for today.
        """
        # Note: In a real-world scenario, we might need to handle date formatting
        # or different URLs for different regions.
        racecards_url = f"{self.BASE_URL}/racecards/"
        html_content = self.fetcher.fetch(racecards_url)
        if not html_content:
            return []
        return self._parse_races(html_content)

    def _parse_races(self, html_content: str) -> List[Race]:
        """Parses races from the HTML content."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')
        race_data_json = self._extract_race_data_json(html_content)
        if not race_data_json:
            # Fallback or logging if the main JSON blob isn't found
            logging.warning(f"{self.SOURCE_ID}: Could not find main JSON data blob.")
            return []

        races = []
        # This logic is transplanted from the legacy adapter and adapted for V7 models
        # It's simplified and targets the main race card structure.
        race_containers = soup.select('div.RC-meetingDay__race')
        for race_container in race_containers:
            try:
                race_id = race_container.get('data-diffusion-race-id')
                track_name = race_data_json.get('location', {}).get('name', 'Unknown Track')

                # Extract race number from a potential title attribute or other source if available
                race_time_element = race_container.select_one('span.RC-raceTime')
                race_number = None
                if race_time_element and race_time_element.has_attr('data-race-time-long'):
                    # This is a guess, might need refinement based on actual page structure
                    # For now, we can't reliably get the race number from the card overview.
                    pass

                runners = []
                runner_rows = race_container.select('div.RC-runnerRow')
                for row in runner_rows:
                    if 'RC-runnerRow_disabled' in row.get('class', []):
                        continue

                    program_number_span = row.select_one('span.RC-runnerNumber__no')
                    program_number = int(program_number_span.text.strip()) if program_number_span else None

                    runner_name_a = row.select_one('a.RC-runnerName')
                    runner_name = runner_name_a.text.strip() if runner_name_a else "Unknown Runner"

                    # Odds are not easily available on the main racecard view in a structured way.
                    # A more complex implementation would fetch each race detail page.
                    # For this refit, we will omit odds, as the legacy adapter did.

                    runners.append(Runner(
                        name=runner_name,
                        program_number=program_number
                    ))

                if race_id and runners:
                    races.append(Race(
                        race_id=race_id,
                        track_name=track_name,
                        race_number=race_number,
                        runners=runners
                    ))
            except Exception as e:
                logging.error(f"{self.SOURCE_ID}: Error parsing a race container: {e}")
                continue
        return races

    def _extract_race_data_json(self, html_content: str) -> dict:
        """Extracts the main JSON data blob from the page's script tags."""
        match = re.search(r'rp_config_\.page\s*=\s*({.*?});', html_content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logging.error(f"{self.SOURCE_ID}: Failed to decode JSON from rp_config.")
                return {}
        return {}
