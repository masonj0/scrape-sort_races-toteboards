import re
from datetime import datetime
from typing import Any, List, Dict

from bs4 import BeautifulSoup

from ..fetcher import get_page_content
from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from .utils import get_datetime_from_string, _convert_odds_to_float


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
            except Exception as e:
                print(f"Error processing race at {race_details['url']}: {e}")
        return races

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """Parses the HTML content to extract race data."""
        if not html_content:
            return []

        # This method is for offline parsing, so we need to extract details from the single page
        soup = BeautifulSoup(html_content, 'lxml')
        header_tag = soup.select_one("div.race-header h1")
        if not header_tag:
            return []
        header_text = header_tag.text.strip()
        time_match = re.search(r'(\d{2}:\d{2})', header_text)
        post_time_str = time_match.group(1) if time_match else ""
        track_match = re.search(r'\d{2}:\d{2}\s(.*?)\s\d{2}', header_text)
        track_name = track_match.group(1).strip() if track_match else "Unknown"

        race_details = {
            "course": track_name,
            "time": post_time_str,
            "name": soup.select_one("h2.h7").text.strip(),
            "url": "", # No URL available in this context
            "race_number": 0 # No race number available in this context
        }

        race = self._parse_race(html_content, race_details)
        return [race] if race else []


    def _get_race_details(self, html_content: str) -> List[Dict]:
        """
        Parses the racecards index page to get the URLs and other details for each race.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        races = []

        # Find all meeting sections
        for meeting_section in soup.select("section.panel"):
            # Extract course name from the meeting section header
            course_name_tag = meeting_section.select_one("h2.h6")
            if course_name_tag:
                course_name = course_name_tag.text.strip().replace(" Racecards", "")
            else:
                continue

            # Find all race entries within the meeting section
            for race_entry in meeting_section.select("div.meeting-list-entry"):
                race_link_tag = race_entry.select_one("a.a--plain")
                if race_link_tag and race_link_tag.has_attr('href'):
                    url = self.BASE_URL + race_link_tag['href']

                    # Extract race number
                    race_number_tag = race_entry.select_one("span.post__number")
                    race_number = int(race_number_tag.text.strip()) if race_number_tag else 0

                    # Extract race time and name
                    h7_tag = race_entry.select_one("span.h7")
                    if h7_tag:
                        full_title = h7_tag.text.strip()
                        time_match = re.search(r"(\d{2}:\d{2})", full_title)
                        time = time_match.group(1) if time_match else ""
                        name = re.sub(r"^\d{2}:\d{2}\s-\s", "", full_title).strip()
                    else:
                        time, name = "", ""

                    races.append({
                        "course": course_name,
                        "time": time,
                        "name": name,
                        "url": url,
                        "race_number": race_number
                    })
        return races

    def _parse_race(self, html_content: str, race_details: Dict) -> NormalizedRace:
        """
        Parses the HTML of a single race page to extract race and runner information.
        """
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
                post_time = get_datetime_from_string(dt_str)
            except ValueError:
                post_time = None

        race_info_tag = soup.select_one("div.race-info div")
        race_type = race_info_tag.text.strip() if race_info_tag else "Unknown"

        runners = []
        for card in soup.select("div.runner-card"):
            horse_name_tag = card.select_one(".horse-name a")
            if not horse_name_tag:
                continue

            name = horse_name_tag.text.strip()

            number_tag = card.select_one(".runner-number")
            number = int(number_tag.text.strip()) if number_tag else 0

            jockey_tag = card.select_one(".jockey")
            jockey = jockey_tag.text.strip().replace("J: ", "") if jockey_tag else ""

            trainer_tag = card.select_one(".trainer")
            trainer = trainer_tag.text.strip().replace("T: ", "") if trainer_tag else ""

            odds_tag = card.select_one(".odds")
            odds = odds_tag.text.strip() if odds_tag else ""

            runners.append(
                NormalizedRunner(
                    name=name,
                    program_number=number,
                    jockey=jockey,
                    trainer=trainer,
                    odds=_convert_odds_to_float(odds)
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
