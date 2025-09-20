#!/usr/bin/env python3
"""
A V3-compliant adapter for TwinSpires, based on direct reconnaissance.
This adapter uses a two-stage scraping process to acquire race data.
"""
import anyio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..fetcher import get_page_content
from bs4 import BeautifulSoup

class TwinSpiresAdapter(BaseAdapterV3):
    """ An adapter for the TwinSpires website. """

    SOURCE_ID = "twinspires"
    BASE_URL = "https://www.twinspires.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def fetch(self) -> List[NormalizedRace]:
        """ Fetches all race data using a two-stage process. """
        index_url = f"{self.BASE_URL}/adw/todays-tracks?sortOrder=nextUp"
        logging.info(f"Fetching race index from: {index_url}")
        index_html = await get_page_content(index_url)

        if not index_html:
            logging.warning("Failed to fetch TwinSpires race index.")
            return []

        soup = BeautifulSoup(index_html, 'html.parser')
        race_links = []
        for link in soup.find_all('a', href=lambda h: h and '/race/' in h and '/results/' not in h):
            race_links.append(self.BASE_URL + link['href'])

        if not race_links:
            logging.warning("No race links found on TwinSpires index page.")
            return []

        logging.info(f"Found {len(race_links)} races. Fetching details concurrently...")

        results_map = {}
        async with anyio.create_task_group() as tg:
            for link in race_links:
                async def work(url):
                    results_map[url] = await get_page_content(url)

                tg.start_soon(work, link)

        successful_htmls = [html for html in results_map.values() if isinstance(html, str)]
        return self._parse_race_detail_pages(successful_htmls)

    def _parse_race_detail_pages(self, race_htmls: list[str]) -> list[NormalizedRace]:
        """ Parses a list of race detail HTML snippets. """
        all_races = []
        for html in race_htmls:
            try:
                race = self._parse_single_race_detail(html)
                if race:
                    all_races.append(race)
            except Exception as e:
                logging.warning(f"Skipping a malformed race detail page in TwinSpires parse: {e}", exc_info=True)
                continue
        return all_races

    def _parse_single_race_detail(self, html: str) -> Optional[NormalizedRace]:
        """ Parses a single race detail HTML page. """
        soup = BeautifulSoup(html, 'html.parser')

        header = soup.find('div', class_='race-title')
        if not header: return None

        track_name = header.find('a').text.strip()
        race_number_text = header.find('strong').text
        race_number = int(''.join(filter(str.isdigit, race_number_text)))

        # A full implementation would parse post time, distance, etc.
        # Using a placeholder for now.
        post_time = datetime.now()

        runners = []
        program = soup.find('div', id='program')
        if not program: return None

        for i, runner_row in enumerate(program.find_all('div', class_='runner-wrapper')):
            name_tag = runner_row.find('div', class_='runner-name')
            if not name_tag: continue
            name = name_tag.text.strip()

            odds_span = runner_row.find('span', class_='odds')
            odds_str = odds_span.text.strip() if odds_span else None

            if not odds_str: continue

            try:
                if '/' in odds_str:
                    num, den = map(int, odds_str.split('/'))
                    if den == 0: continue
                    odds = (num / den) + 1.0
                else:
                    odds = float(odds_str) + 1.0

                runners.append(NormalizedRunner(
                    name=name,
                    odds=odds,
                    program_number=i + 1 # Program number is based on order
                ))
            except (ValueError, TypeError):
                continue

        if not runners:
            return None

        race_id = f"{track_name.replace(' ', '')}-{race_number}"

        return NormalizedRace(
            race_id=race_id,
            track_name=track_name,
            race_number=race_number,
            post_time=post_time,
            number_of_runners=len(runners),
            runners=runners
        )

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """
        Parses a single page containing multiple race summaries.
        Not used by this adapter's two-stage fetch process.
        """
        return []
