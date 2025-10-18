import re
from datetime import datetime
from typing import List, Dict

from bs4 import BeautifulSoup

from ..fetcher import get_page_content
from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner

def _convert_odds_to_float(odds_str: str) -> float:
    """Converts odds string to a float. Handles 'EVS' and fractions."""
    if isinstance(odds_str, str):
        odds_str = odds_str.strip().upper()
        if odds_str == 'EVS':
            return 2.0
        if '/' in odds_str:
            try:
                num, den = map(int, odds_str.split('/'))
                return (num / den) + 1.0
            except (ValueError, ZeroDivisionError):
                return 0.0
    return 0.0

class AtTheRacesAdapter(BaseAdapterV3):
    """
    Adapter for attheraces.com.
    """
    SOURCE_ID = 'attheraces'
    BASE_URL = "https://www.attheraces.com"

    def __init__(self, cache_dir: str = None):
        super().__init__(cache_dir)

    async def fetch(self) -> List[NormalizedRace]:
        """Fetches data from attheraces.com."""
        index_content = await get_page_content(f"{self.BASE_URL}/racecards")
        race_details_list = self._get_race_details(index_content)

        races = []
        for race_details in race_details_list:
            try:
                race_content = await get_page_content(race_details["url"])
                race = self._parse_race(race_content, race_details)
                if race:
                    races.append(race)
            except Exception:
                continue
        return races

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """This adapter is designed for live fetching, so offline parsing is not supported."""
        return []

    def _get_race_details(self, html_content: str) -> List[Dict]:
        """
        Parses the racecards index page to get the URLs and other details for each race.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        races = []

        for meeting_section in soup.select("section.panel"):
            course_name_tag = meeting_section.select_one("h2.h6")
            if not course_name_tag:
                continue
            course_name = course_name_tag.text.strip().replace(" Racecards", "")

            for race_entry in meeting_section.select("div.meeting-list-entry"):
                race_link_tag = race_entry.select_one("a.a--plain")
                if not (race_link_tag and race_link_tag.has_attr('href')):
                    continue

                url = self.BASE_URL + race_link_tag['href']
                race_number_tag = race_entry.select_one("span.post__number")
                race_number = int(race_number_tag.text.strip()) if race_number_tag else 0

                h7_tag = race_entry.select_one("span.h7")
                if h7_tag:
                    full_title = h7_tag.text.strip()
                    time_match = re.search(r"(\d{2}:\d{2})", full_title)
                    time = time_match.group(1) if time_match else ""
                else:
                    time = ""

                races.append({"course": course_name, "time": time, "url": url, "race_number": race_number})
        return races

    def _parse_race(self, html_content: str, race_details: Dict) -> NormalizedRace:
        soup = BeautifulSoup(html_content, 'lxml')

        header_tag = soup.select_one("div.race-header h1")
        if not header_tag:
            return None

        header_text = header_tag.text.strip()
        date_match = re.search(r'(\d{2}\s\w{3}\s\d{4})', header_text)
        date_str = date_match.group(1) if date_match else ""

        post_time = None
        if race_details["time"] and date_str:
            try:
                dt_str = f"{date_str} {race_details['time']}"
                post_time = datetime.strptime(dt_str, '%d %b %Y %H:%M')
            except ValueError:
                post_time = None

        race_info_tag = soup.select_one("div.race-info div")
        race_type = race_info_tag.text.strip() if race_info_tag else "Unknown"

        runners = []
        for card in soup.select("div.runner-card"):
            horse_name_tag = card.select_one(".horse-name a")
            if not horse_name_tag:
                continue

            odds_tag = card.select_one(".odds")

            runners.append(
                NormalizedRunner(
                    name=horse_name_tag.text.strip(),
                    odds=_convert_odds_to_float(odds_tag.text.strip() if odds_tag else ""),
                    program_number=int(card.select_one(".runner-number").text.strip())
                )
            )

        return NormalizedRace(
            race_id=f"{race_details['course'].replace(' ', '')}_{race_details['time'].replace(':', '')}",
            track_name=race_details['course'],
            race_number=race_details['race_number'],
            post_time=post_time,
            race_type=race_type,
            number_of_runners=len(runners),
            runners=runners
        )
