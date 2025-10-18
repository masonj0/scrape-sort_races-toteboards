import asyncio
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..http_client import ForagerClient
from .utils import _convert_odds_to_float

class TimeformAdapter(BaseAdapterV3):
    """
    Adapter for timeform.com.
    This adapter implements a three-stage "drill-down" to fetch all race data.
    1. Fetch the main racecards page.
    2. Extract links to all of today's meetings.
    3. Concurrently fetch all race detail pages.
    4. Parse each detail page to extract runner information.
    """
    SOURCE_ID = "timeform"
    BASE_URL = "https://www.timeform.com"

    def __init__(self, config=None):
        super().__init__(config)
        self.forager = ForagerClient()

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches all race data by first getting the summary page to find
        race links, then fetching each of those pages concurrently.
        """
        index_url = f"{self.BASE_URL}/horse-racing/racecards"
        index_html = await self.forager.fetch(index_url)
        if not index_html:
            logging.warning("Failed to fetch the Timeform racecards index page.")
            return []

        race_links = self._extract_race_links(index_html)
        if not race_links:
            logging.warning("No race links found on the Timeform index page.")
            return []

        tasks = [self.forager.fetch(url) for url in race_links]
        race_html_pages = await asyncio.gather(*tasks)

        all_races = []
        for html, url in zip(race_html_pages, race_links):
            if html:
                race = self.parse_race_details(html, url)
                if race:
                    all_races.append(race)
        return all_races

    def _extract_race_links(self, html_content: str) -> List[str]:
        """Extracts all individual race links from the main racecards page."""
        soup = BeautifulSoup(html_content, 'lxml')
        links = []
        for link in soup.select("ul.w-racecard-grid-meeting-races-compact li a"):
            href = link.get("href")
            if href:
                links.append(urljoin(self.BASE_URL, href))
        return links

    def parse_race_details(self, html_content: str, url: str) -> Optional[NormalizedRace]:
        """Parses the race detail page to extract all available data."""
        soup = BeautifulSoup(html_content, 'lxml')

        header = soup.select_one("div.rp-race-card-header h1")
        if not header:
            return None

        header_text = header.get_text(strip=True)
        time_match = re.search(r"(\d{2}:\d{2})", header_text)
        if not time_match:
            return None

        race_time_str = time_match.group(1)
        track_name = header_text.replace(race_time_str, "").strip()

        runners = []
        for runner_item in soup.select("li.rp-race-card__runner"):
            saddle_cloth_tag = runner_item.select_one(".rp-race-card__runner__saddle-cloth")
            name_tag = runner_item.select_one(".rp-race-card__runner__name")
            odds_tag = runner_item.select_one(".rp-race-card__runner__odds")

            if not all([saddle_cloth_tag, name_tag, odds_tag]):
                continue

            runners.append(
                NormalizedRunner(
                    program_number=int(saddle_cloth_tag.get_text(strip=True)),
                    name=name_tag.get_text(strip=True),
                    odds=_convert_odds_to_float(odds_tag.get_text(strip=True)),
                )
            )

        if not runners:
            return None

        try:
            post_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            post_time = None

        return NormalizedRace(
            race_id=url,
            track_name=track_name,
            race_number=0, # Not available on detail page in this format
            post_time=post_time,
            runners=runners,
            number_of_runners=len(runners),
        )

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """
        This method is required by the BaseAdapterV3 interface, but is not
        used by the new drill-down fetch logic.
        """
        pass
