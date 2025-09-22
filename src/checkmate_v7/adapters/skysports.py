import logging
import re
from datetime import date, datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from ..base import BaseAdapterV7
from ..models import Race, Runner


def _convert_odds_to_float(odds_str: Optional[str]) -> Optional[float]:
    """Converts fractional or decimal odds string to a float."""
    if not odds_str or not isinstance(odds_str, str):
        return None

    odds_str = odds_str.strip().upper()
    if odds_str == 'SP':
        return None
    if odds_str == 'EVENS':
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
        # Handle decimal odds that might be provided
        return float(odds_str)
    except (ValueError, TypeError):
        return None


class SkySportsAdapter(BaseAdapterV7):
    """
    Adapter for skysports.com, adapted from the V3 'paddock_parser' version.
    This adapter is synchronous and uses the new multi-stage DefensiveFetcher.
    """

    SOURCE_ID = "skysports"
    BASE_URL = "https://www.skysports.com"

    def fetch_races(self) -> List[Race]:
        """
        Fetches all race data by first getting the summary page to find
        race links, then fetching each of those pages sequentially.
        """
        index_page_url = f"{self.BASE_URL}/racing/racecards"
        logging.info(f"Fetching Sky Sports index page: {index_page_url}")

        index_html = self.fetcher.get(index_page_url, response_type='text')

        if not index_html:
            logging.error("Failed to get valid HTML content from Sky Sports index.")
            return []

        soup = BeautifulSoup(index_html, "lxml")
        meeting_blocks = soup.select("div.sdc-site-concertina-block")
        logging.info(f"Found {len(meeting_blocks)} meeting blocks on Sky Sports.")

        all_races = []
        for meeting_block in meeting_blocks:
            track_name_tag = meeting_block.select_one("h3.sdc-site-concertina-block__title > span.sdc-site-concertina-block__title")
            track_name = track_name_tag.text.strip() if track_name_tag else "Unknown Track"

            race_urls = []
            for event in meeting_block.select("div.sdc-site-racing-meetings__event"):
                link_tag = event.select_one("a.sdc-site-racing-meetings__event-link")
                if link_tag and link_tag.get("href"):
                    race_urls.append(f"{self.BASE_URL}{link_tag['href']}")

            logging.info(f"Found {len(race_urls)} race URLs for track: {track_name}")

            for i, url in enumerate(race_urls):
                logging.info(f"Fetching race detail page: {url}")
                detail_html = self.fetcher.get(url, response_type='text')

                if detail_html:
                    race = self._parse_race_details(detail_html, url, track_name, i + 1)
                    if race:
                        all_races.append(race)
                else:
                    logging.warning(f"Failed to fetch or get text for race detail page: {url}")

        return all_races

    def _parse_race_details(
        self, html_content: str, url: str, track_name: str, race_number: int
    ) -> Optional[Race]:
        """Parses the race detail page to extract all available data."""
        soup = BeautifulSoup(html_content, "lxml")
        try:
            header_tag = soup.select_one("h2.sdc-site-racing-header__name")
            header_text = header_tag.text.strip() if header_tag else ""

            post_time_match = re.search(r"(\d{2}:\d{2})", header_text)
            post_time_str = post_time_match.group(1) if post_time_match else "00:00"

            post_time_dt = datetime.combine(
                date.today(), datetime.strptime(post_time_str, "%H:%M").time()
            )

            runners_list = []
            runner_items = soup.select("div.sdc-site-racing-card__item")
            for item in runner_items:
                name_tag = item.select_one("h4.sdc-site-racing-card__name a")
                program_number_tag = item.select_one("div.sdc-site-racing-card__number strong")
                odds_tag = item.select_one(".sdc-site-racing-card__betting-odds")
                jockey_tag = item.select_one("div.sdc-site-racing-card__jockey a")
                trainer_tag = item.select_one("div.sdc-site-racing-card__trainer a")


                name = name_tag.text.strip() if name_tag else None
                program_number_str = program_number_tag.text.strip() if program_number_tag else None
                odds_str = odds_tag.text.strip() if odds_tag else None

                # This is the critical enhancement: getting the odds
                odds_float = _convert_odds_to_float(odds_str)

                if name and program_number_str:
                    runners_list.append(
                        Runner(
                            name=name,
                            program_number=program_number_str.strip(),
                            odds=odds_float,
                            jockey=jockey_tag.text.strip() if jockey_tag else None,
                            trainer=trainer_tag.text.strip() if trainer_tag else None,
                        )
                    )

            if not runners_list:
                return None

            path_parts = [part for part in url.split("/") if part]
            race_id = f"{self.SOURCE_ID}_{track_name.replace(' ', '')}_{path_parts[-1]}"

            return Race(
                race_id=race_id,
                track_name=track_name,
                post_time=post_time_dt,
                race_number=race_number,
                race_type="Thoroughbred", # Assumption from source
                runners=runners_list,
                number_of_runners=len(runners_list),
            )

        except Exception as e:
            logging.error(f"Error parsing race details from {url}: {e}", exc_info=True)
            return None
