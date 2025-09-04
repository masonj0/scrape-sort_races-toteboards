import asyncio
import logging
import re
from datetime import date, datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..http_client import ForagerClient


class SkySportsAdapter(BaseAdapterV3):
    """
    Adapter for skysports.com.
    Fetches the main racecards page to find individual race URLs,
    then fetches each race detail page to extract full runner information.
    """

    SOURCE_ID = "skysports"

    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://www.skysports.com"
        self.forager = ForagerClient()

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches all race data by first getting the summary page to find
        race links, then fetching each of those pages concurrently.
        """
        index_page_url = f"{self.base_url}/racing/racecards"
        index_html = await self.forager.fetch(index_page_url)
        if not index_html:
            logging.warning("Failed to fetch the racecards index page.")
            return []

        race_urls = self._get_race_detail_urls(index_html)
        if not race_urls:
            logging.warning("No race detail URLs found on the index page.")
            return []

        tasks = [self.forager.fetch(url) for url in race_urls]
        race_html_pages = await asyncio.gather(*tasks)

        races = [
            self._parse_race_details(html, url)
            for html, url in zip(race_html_pages, race_urls)
            if html
        ]
        return [race for race in races if race]

    def _get_race_detail_urls(self, html_content: str) -> List[str]:
        """Parses the index page to find links to individual race pages."""
        soup = BeautifulSoup(html_content, "lxml")
        links = soup.select("a.sdc-site-racing-meetings__event-link")
        return [f"{self.base_url}{link['href']}" for link in links if link.get("href")]

    def _parse_race_details(
        self, html_content: str, url: str
    ) -> Optional[NormalizedRace]:
        """Parses the race detail page to extract all available data."""
        soup = BeautifulSoup(html_content, "lxml")

        try:
            header_tag = soup.select_one("h2.sdc-site-racing-header__name")
            header_text = header_tag.text.strip() if header_tag else ""

            race_time_match = re.search(r"(\d{2}:\d{2})", header_text)
            race_time_str = race_time_match.group(1) if race_time_match else "00:00"

            track_name = header_text.replace(race_time_str, "").strip()

            post_time_dt = datetime.combine(
                date.today(), datetime.strptime(race_time_str, "%H:%M").time()
            )

            runners_list = []
            runner_items = soup.select("div.sdc-site-racing-card__item")
            for i, item in enumerate(runner_items):
                name_tag = item.select_one("h4.sdc-site-racing-card__name a")
                program_number_tag = item.select_one("div.sdc-site-racing-card__number strong")

                name = name_tag.text.strip() if name_tag else None
                program_number_str = program_number_tag.text.strip() if program_number_tag else str(i + 1)

                if name:
                    try:
                        program_number = int(re.search(r'\d+', program_number_str).group())
                    except (ValueError, AttributeError):
                        program_number = i + 1

                    runners_list.append(
                        NormalizedRunner(name=name, program_number=program_number)
                    )

            race_number_match = re.search(r"race-(\d+)", url, re.IGNORECASE)
            race_number = int(race_number_match.group(1)) if race_number_match else 1

            return NormalizedRace(
                race_id=url.split("/")[-1],
                track_name=track_name,
                post_time=post_time_dt,
                race_number=race_number,
                runners=runners_list,
                number_of_runners=len(runners_list),
            )

        except Exception as e:
            logging.error(f"Error parsing race details from {url}: {e}")
            return None

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """This method is not used in the new V3 flow but is required by the base class."""
        return []
