#!/usr/bin/env python3
"""
A V3-compliant adapter for TwinSpires, based on all verified reconnaissance.
This adapter uses a two-stage scraping process to acquire race data.
"""
import asyncio
from datetime import datetime, date
from paddock_parser.base import BaseAdapterV3
from paddock_parser.models import NormalizedRace, NormalizedRunner
from paddock_parser.fetcher import get_page_content
from bs4 import BeautifulSoup

class TwinSpiresAdapter(BaseAdapterV3):
    """ An adapter for the TwinSpires website. """

    BASE_URL = "https://www.twinspires.com"

    async def fetch(self) -> list[NormalizedRace]:
        """ Fetches all race data using a CORRECT two-stage process. """

        # Stage 1: Get the master list of race URLs from the "Today's Tracks" index page
        index_url = f"{self.BASE_URL}/adw/todays-tracks?sortOrder=nextUp"
        index_html = await get_page_content(index_url)

        if not index_html:
            return []

        soup = BeautifulSoup(index_html, 'html.parser')
        race_links = [self.BASE_URL + link['href'] for link in soup.find_all('a', href=lambda h: h and '/race/' in h and '/results/' not in h)]

        if not race_links:
            return []

        # Stage 2: Concurrently fetch the HTML details for every race link found
        tasks = [get_page_content(link) for link in race_links]
        race_htmls = await asyncio.gather(*tasks, return_exceptions=True)

        successful_htmls = [html for html in race_htmls if isinstance(html, str)]
        return self.parse_races(successful_htmls)

    def parse_races(self, race_htmls: list[str]) -> list[NormalizedRace]:
        """ Parses a list of individual race detail HTML pages. """
        all_races = []
        for html in race_htmls:
            try:
                soup = BeautifulSoup(html, 'html.parser')

                # These selectors are based on real reconnaissance
                header = soup.find('div', class_='race-title')
                track_name = header.find('a').text.strip()
                race_number_text = header.find('strong').text
                race_number = int(''.join(filter(str.isdigit, race_number_text)))

                runners = []
                program = soup.find('div', id='program')
                for i, runner_row in enumerate(program.find_all('div', class_='runner-wrapper')):
                    name = runner_row.find('div', class_='runner-name').text.strip()
                    odds_span = runner_row.find('span', class_='odds')
                    odds_str = odds_span.text.strip() if odds_span else "0"

                    try:
                        if '/' in odds_str:
                            num, den = map(int, odds_str.split('/'))
                            odds = num / den
                        else:
                            odds = float(odds_str)
                        runners.append(NormalizedRunner(name=name))
                    except ValueError:
                        continue

                if runners:
                    all_races.append(NormalizedRace(
                        track=track_name,
                        race_number=race_number,
                        race_time=datetime.now(), # Placeholder - needs real parsing
                        runners=runners
                    ))
            except Exception as e:
                print(f"Skipping a malformed TwinSpires detail page: {e}")
                continue

        return all_races
