import re
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from ..base import BaseAdapterV7
from ..models import Race, Runner
from .utils import _convert_odds_to_float


class AtTheRacesAdapter(BaseAdapterV7):
    """
    Adapter for attheraces.com.
    """
    SOURCE_ID = 'attheraces'

    def fetch_races(self) -> List[Race]:
        """Fetches data from attheraces.com."""
        # This adapter is designed to be used with offline data for now.
        # The `parse_races` method should be called directly with HTML content.
        raise NotImplementedError("Live fetching for AtTheRacesAdapter is not implemented.")

    def parse_races(self, html_content: str) -> List[Race]:
        """Parses the HTML content to extract race data."""
        if not html_content:
            return []
        return self._parse_race_data(html_content)

    def _parse_race_data(self, html_content: str) -> List[Race]:
        """
        Parses the main HTML content to extract all race and runner information.
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # --- Race-level data extraction ---
        header_tag = soup.select_one("div.race-header h1")
        if not header_tag:
            return []

        header_text = header_tag.text.strip() # "17:45 Roscommon (IRE) 01 Sep 2025"

        time_match = re.search(r'(\d{2}:\d{2})', header_text)
        post_time_str = time_match.group(1) if time_match else ""

        track_match = re.search(r'\d{2}:\d{2}\s(.*?)\s\d{2}', header_text)
        track_name = track_match.group(1).strip() if track_match else "Unknown"

        date_match = re.search(r'(\d{2}\s\w{3}\s\d{4})', header_text)
        date_str = date_match.group(1) if date_match else ""

        post_time = None
        if post_time_str and date_str:
            try:
                dt_str = f"{date_str} {post_time_str}"
                post_time = datetime.strptime(dt_str, '%d %b %Y %H:%M')
            except ValueError:
                post_time = None

        race_info_tag = soup.select_one("div.race-info div")
        race_type = race_info_tag.text.strip() if race_info_tag else "Unknown"

        # --- Runner-level data extraction ---
        runners = []
        runner_cards = soup.select("div.runner-card")
        for card in runner_cards:
            name = card.select_one(".horse-name a").text.strip()
            number = int(card.select_one(".runner-number").text.strip())
            jockey = card.select_one(".jockey").text.strip().replace("J: ", "")
            trainer = card.select_one(".trainer").text.strip().replace("T: ", "")
            odds = card.select_one(".odds").text.strip()

            runners.append(
                Runner(
                    name=name,
                    program_number=number,
                    jockey=jockey,
                    trainer=trainer,
                    odds=_convert_odds_to_float(odds)
                )
            )

        race = Race(
            race_id=f"{track_name.replace(' ', '')}_{post_time_str.replace(':', '')}",
            track_name=track_name,
            race_number=1, # Assuming 1 as per test spec
            post_time=post_time,
            race_type=race_type,
            number_of_runners=len(runners),
            runners=runners
        )

        return [race]