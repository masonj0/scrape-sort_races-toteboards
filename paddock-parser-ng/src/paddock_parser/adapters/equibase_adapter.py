from paddock_parser.adapters.base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from bs4 import BeautifulSoup
import re
from typing import List

class EquibaseAdapter(BaseAdapterV3):
    """
    Adapter for equibase.com, parsing data from offline HTML samples.
    """
    SOURCE_ID = "equibase"

    def __init__(self, config=None):
        super().__init__(config)
        # Offline adapter

    async def fetch(self) -> List[NormalizedRace]:
        """This is an offline adapter and should not be fetched by the pipeline."""
        raise NotImplementedError("EquibaseAdapter is an offline adapter and does not support live fetching.")

    def parse_races(self, html_content: str) -> list[NormalizedRace]:
        """Public method to parse races, fulfilling the BaseAdapterV3 contract."""
        return self._parse_racecard(html_content)

    def _parse_racecard(self, html_content: str) -> list[NormalizedRace]:
        """
        Parses the HTML content of a Equibase race card page.
        This implementation is specifically tailored to the structure of the
        provided `equibase_sample.html` fixture.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')

        # Extract track name from the h1 tag
        track_name_tag = soup.select_one('h1#pageHeader')
        if track_name_tag and 'Entries' in track_name_tag.text:
            track_name_text = track_name_tag.text.replace('\n', '').strip()
            track_name = track_name_text.split(' Entries')[0]
        else:
            track_name = "Unknown Track"

        races = []
        race_table = soup.select_one('table#entryRaces tbody.results')
        if not race_table:
            return []

        for row in race_table.select('tr'):
            cells = row.select('td')
            if len(cells) < 7:
                continue

            try:
                race_number = int(cells[0].text.strip())
                purse_text = cells[1].text.strip().replace('$', '').replace(',', '')
                purse = int(purse_text) if purse_text.isdigit() else 0
                race_type = cells[2].text.strip()
                distance = cells[3].text.strip()
                surface = cells[4].text.strip()
                starters = int(cells[5].text.strip())

                race = NormalizedRace(
                    race_id=f"{track_name.replace(' ', '')}-{race_number}",
                    track_name=track_name,
                    race_number=race_number,
                    race_type=race_type,
                    number_of_runners=starters,
                    runners=[] # Runner details are not on this page
                )
                races.append(race)
            except (ValueError, IndexError):
                continue # Skip rows that don't have the expected data

        return races
