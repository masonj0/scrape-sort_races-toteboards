"""
The new, modern TwinSpires adapter.
"""
from typing import List, Optional
from datetime import datetime
import logging

import anyio
from bs4 import BeautifulSoup

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner


class TwinspiresModernAdapter(BaseAdapterV7):
    """
    Adapter for the TwinSpires website (two-stage scrape).
    This is the modern implementation, refactored into its own module.
    """
    SOURCE_ID = "twinspires"
    BASE_URL = "https://www.twinspires.com"

    async def fetch_races(self) -> List[Race]:
        """Fetches all race data using a two-stage process."""
        index_url = f"{self.BASE_URL}/adw/todays-tracks?sortOrder=nextUp"
        index_html = await self.fetcher.fetch(index_url, response_type='text')
        if not index_html:
            return []

        detail_links = self._parse_race_links(index_html)
        if not detail_links:
            return []

        # Fetch all detail pages concurrently
        detail_pages_html = []
        async def fetch_and_store(link):
            html = await self.fetcher.fetch(link, response_type='text')
            if html:
                detail_pages_html.append(html)

        async with anyio.create_task_group() as tg:
            for link in detail_links:
                tg.start_soon(fetch_and_store, link)

        # Parse the results
        all_races = []
        for html in detail_pages_html:
            if html:
                try:
                    race = self._parse_single_race_detail(html)
                    if race:
                        all_races.append(race)
                except Exception as e:
                    logging.warning(f"{self.SOURCE_ID}: Skipping a malformed race detail page: {e}")
                    continue
        return all_races

    def _parse_race_links(self, html_content: str) -> List[str]:
        """Parses the index page to find links to all race detail pages."""
        soup = BeautifulSoup(html_content, 'html.parser')
        # Use set to find unique links, then convert to list
        race_links = set()
        for link in soup.find_all('a', href=lambda h: h and '/races/' in h and '/results/' not in h):
            race_links.add(self.BASE_URL + link['href'])
        return list(race_links)

    def _parse_single_race_detail(self, html: str) -> Optional[Race]:
        """Parses a single race detail HTML page."""
        soup = BeautifulSoup(html, 'html.parser')

        header = soup.find('div', class_='race-title')
        if not header: return None

        track_name = header.find('a').text.strip()
        race_number_text = header.find('strong').text
        race_number = int(''.join(filter(str.isdigit, race_number_text)))

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
                # Convert fractional odds like "5/2" to decimal
                if '/' in odds_str:
                    num, den = map(int, odds_str.split('/'))
                    odds = (num / den) + 1.0 if den != 0 else None
                # Handle simple integer odds
                else:
                    odds = float(odds_str) + 1.0

                if odds is not None:
                    runners.append(Runner(
                        name=name,
                        odds=odds,
                        program_number=i + 1
                    ))
            except (ValueError, TypeError):
                continue

        if not runners:
            return None

        return Race(
            race_id=f"{self.SOURCE_ID}_{track_name.replace(' ', '')}_{race_number}",
            track_name=track_name,
            race_number=race_number,
            runners=runners
        )
