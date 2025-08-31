import asyncio
import re
from typing import List, Optional

from bs4 import BeautifulSoup

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..http_client import ForagerClient


class SkySportsAdapter(BaseAdapterV3):
    """
    Adapter for skysports.com, using a 'Minimalist Scraper' approach.
    Fetches only the summary racecard page to quickly identify races with small fields.
    """

    SOURCE_ID = "skysports"

    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://www.skysports.com/racing/racecards"
        self.forager = ForagerClient()

    async def fetch(self) -> List[NormalizedRace]:
        """Fetches the main racecards page and parses the summary data."""
        html_content = await self.forager.fetch(self.base_url)
        if not html_content:
            return []
        return self._parse_race_summaries(html_content)

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """
        Parses the HTML content to extract race summaries.
        """
        return self._parse_race_summaries(html_content)

    def _parse_race_summaries(self, html_content: str) -> List[NormalizedRace]:
        """Parses the summary page to extract track names, times, and runner counts."""
        from datetime import datetime, date

        soup = BeautifulSoup(html_content, "lxml")
        races = []

        meeting_blocks = soup.select("div.sdc-site-concertina-block")

        for block in meeting_blocks:
            track_name_tag = block.select_one("h3.sdc-site-concertina-block__title > span.sdc-site-concertina-block__title")
            if not track_name_tag:
                continue
            track_name = track_name_tag.text.strip()

            race_events = block.select("div.sdc-site-racing-meetings__event")
            for i, event in enumerate(race_events):
                time_tag = event.select_one("span.sdc-site-racing-meetings__event-time")
                race_name_tag = event.select_one("span.sdc-site-racing-meetings__event-name")
                details_tag = event.select_one("span.sdc-site-racing-meetings__event-details")

                if time_tag and race_name_tag and details_tag:
                    race_time_str = time_tag.text.strip()
                    race_name = race_name_tag.text.strip()
                    details_text = details_tag.text.strip()

                    race_number_from_name = self._parse_race_number_from_name(race_name)
                    race_number = int(race_number_from_name) if race_number_from_name else i + 1

                    runner_count = self._parse_runner_count(details_text)

                    try:
                        post_time_dt = datetime.combine(date.today(), datetime.strptime(race_time_str, "%H:%M").time())
                    except ValueError:
                        post_time_dt = None

                    races.append(
                        NormalizedRace(
                            race_id=f"{track_name.replace(' ', '')}-{race_time_str}",
                            track_name=track_name,
                            race_number=race_number,
                            post_time=post_time_dt,
                            number_of_runners=runner_count,
                            race_type="T"
                        )
                    )
        return races

    def _parse_runner_count(self, text: str) -> Optional[int]:
        """Extracts the number of runners from a string like '9 Runners'."""
        match = re.search(r"(\d+)\s+Runners", text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                return None
        return None

    def _parse_race_number_from_name(self, text: str) -> Optional[str]:
        """Extracts the race number from a string like 'Race 1 - BetUK...'"""
        match = re.search(r"Race\s+(\d+)", text, re.IGNORECASE)
        if match:
            try:
                return match.group(1)
            except IndexError:
                return None
        return None
