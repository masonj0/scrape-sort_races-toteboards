"""
Adapter for attheraces.com, refactored for Checkmate V7.
"""
import logging
import re
from datetime import datetime
from typing import List, Optional, Dict

from bs4 import BeautifulSoup

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner

def _convert_odds_to_float(odds_str: Optional[str]) -> Optional[float]:
    """Converts fractional odds string to a float."""
    if not odds_str or not isinstance(odds_str, str):
        return None

    odds_str = odds_str.strip().upper()
    if 'EVS' in odds_str:
        return 2.0

    if '/' in odds_str:
        try:
            numerator, denominator = map(int, odds_str.split('/'))
            if denominator == 0:
                return None
            return (numerator / denominator) + 1.0
        except (ValueError, ZeroDivisionError):
            return None
    try:
        # Handle cases like "11.0"
        return float(odds_str) + 1.0
    except (ValueError, TypeError):
        return None

class AtTheRacesAdapter(BaseAdapterV7):
    """
    Adapter for attheraces.com. Fetches an index of races and then scrapes each race page.
    """
    SOURCE_ID = "attheraces"
    BASE_URL = "https://www.attheraces.com"

    def init(self, fetcher: DefensiveFetcher):
        super().init(fetcher)

    def fetch_races(self) -> List[Race]:
        """Fetches all race data using a two-stage process."""
        logging.info(f"{self.SOURCE_ID}: Fetching index page.")
        index_html = self.fetcher.get(f"{self.BASE_URL}/racecards", response_type='text')
        if not index_html:
            logging.warning(f"{self.SOURCE_ID}: Failed to fetch index page.")
            return []

        race_details_list = self._parse_race_links(index_html)
        if not race_details_list:
            logging.warning(f"{self.SOURCE_ID}: No race links found on index page.")
            return []

        all_races = []
        # Limiting to 5 races to be respectful of the source and for speed
        for race_details in race_details_list[:5]:
            url = race_details["url"]
            logging.info(f"{self.SOURCE_ID}: Fetching race detail page: {url}")
            html = self.fetcher.get(url, response_type='text')
            if html:
                try:
                    race = self.parse_single_race_detail(html, race_details)
                    if race:
                        all_races.append(race)
                except Exception as e:
                    logging.warning(f"{self.SOURCE_ID}: Skipping a malformed race detail page {url}: {e}", exc_info=True)
                    continue

        logging.info(f"{self.SOURCE_ID}: Successfully parsed {len(all_races)} races.")
        return all_races

    def _parse_race_links(self, html_content: str) -> List[Dict]:
        """Parses the index page to find links to all race detail pages."""
        soup = BeautifulSoup(html_content, 'html.parser')
        races = []

        # The structure seems to be a section for each meeting
        for meeting_section in soup.select("section.panel"):
            course_name_tag = meeting_section.select_one("h2.h6")
            if not course_name_tag:
                continue
            # Example: "Bath Racecards" -> "Bath"
            course_name = course_name_tag.text.strip().replace(" Racecards", "")

            # Each race is a div inside the meeting section
            for race_entry in meeting_section.select("div.meeting-list-entry"):
                race_link_tag = race_entry.select_one("a.a--plain")
                if not (race_link_tag and race_link_tag.has_attr('href')):
                    continue

                url = self.BASE_URL + race_link_tag['href']

                # Extract time from the title, e.g. "13:50 Sky Sports Racing..."
                h7_tag = race_entry.select_one("span.h7")
                time = ""
                if h7_tag:
                    full_title = h7_tag.text.strip()
                    time_match = re.search(r"(\d{2}:\d{2})", full_title)
                    time = time_match.group(1) if time_match else ""

                races.append({
                    "course": course_name,
                    "time": time,
                    "url": url,
                })
        logging.info(f"{self.SOURCE_ID}: Found {len(races)} race links.")
        return races

    def parse_single_race_detail(self, html_content: str, race_details: Dict) -> Optional[Race]:
        """Parses a single race detail HTML page."""
        soup = BeautifulSoup(html_content, 'html.parser')

        header_tag = soup.select_one("div.race-header h1")
        if not header_tag: return None

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
            name_tag = card.select_one(".horse-name a")
            number_tag = card.select_one(".runner-number")
            jockey_tag = card.select_one(".jockey")
            trainer_tag = card.select_one(".trainer")
            odds_tag = card.select_one(".odds")

            if not all([name_tag, number_tag]):
                continue

            name = name_tag.text.strip()
            number = int(number_tag.text.strip())
            jockey = jockey_tag.text.strip().replace("J: ", "") if jockey_tag else None
            trainer = trainer_tag.text.strip().replace("T: ", "") if trainer_tag else None
            odds_str = odds_tag.text.strip() if odds_tag else None
            odds = _convert_odds_to_float(odds_str)

            if odds is not None:
                runners.append(Runner(
                    name=name,
                    program_number=number,
                    jockey=jockey,
                    trainer=trainer,
                    odds=odds
                ))

        if not runners:
            return None

        # Try to get race number from URL, e.g. /1745
        race_number_match = re.search(r'/(\d{4})$', race_details["url"])
        race_number = int(race_number_match.group(1)) if race_number_match else 1

        return Race(
            race_id=f'{self.SOURCE_ID}{race_details["course"].replace(" ", "")}{race_details["time"].replace(":", "")}',
            track_name=race_details['course'],
            race_number=race_number,
            post_time=post_time,
            race_type=race_type,
            number_of_runners=len(runners),
            runners=runners
        )
