#!/usr/bin/env python3
"""
A V3-compliant adapter for scraping race data from Equibase.
This is the first new adapter of the V4 Polyglot Renaissance.
The core logic is a Python translation of a modern, open-source JavaScript scraper.
"""
from datetime import datetime, date
from paddock_parser.base import BaseAdapterV3
from paddock_parser.models import NormalizedRace, NormalizedRunner
from paddock_parser.fetcher import get_page_content
from bs4 import BeautifulSoup

class EquibaseAdapter(BaseAdapterV3):
    """
    An adapter for fetching and parsing data from www.equibase.com.
    It targets the daily entries pages.
    """

    BASE_URL = "http://www.equibase.com"

    async def fetch(self, fetch_date: date) -> list[NormalizedRace]:
        """ Fetches all race data for a given date from the entries page. """
        date_str = fetch_date.strftime('%m%d%y')
        entries_url = f"{self.BASE_URL}/entries/ENT_{date_str}.html?COUNTRY=USA"

        html_content = await get_page_content(entries_url)

        if not html_content:
            return []

        return self.parse_races(html_content)

    def parse_races(self, html_content: str) -> list[NormalizedRace]:
        """ Parses the full HTML page of daily entries. """
        soup = BeautifulSoup(html_content, 'html.parser')
        all_races = []

        track_tables = soup.find_all('table', summary=lambda s: s and s.startswith('Track Abbr:'))

        for track_table in track_tables:
            try:
                track_name = track_table.find('tr').find('strong').text.strip()
                race_rows = track_table.find_all('tr', class_='entry')

                for race_row in race_rows:
                    links = race_row.find_all('a')
                    if not links:
                        continue

                    race_number_str = links[0].text.strip()
                    race_number = int(''.join(filter(str.isdigit, race_number_str)))

                    # NOTE: A full implementation would require a second, asynchronous
                    # fetch to the race detail page (links[1]['href']) to get runners.
                    # For this first version, we prove the schedule parsing.
                    all_races.append(NormalizedRace(
                        track=track_name,
                        race_number=race_number,
                        race_time=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                        runners=[NormalizedRunner(name="TBD")]
                    ))
            except Exception as e:
                print(f"Skipping a malformed table/row in Equibase parse: {e}")
                continue

        return all_races
