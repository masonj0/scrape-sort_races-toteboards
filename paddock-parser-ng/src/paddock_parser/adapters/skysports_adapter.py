import re
from typing import List

from bs4 import BeautifulSoup

from .base import BaseAdapterV3, NormalizedRace


def parse_race_summaries(html_content: str) -> List[NormalizedRace]:
    """
    Parses the HTML of the Sky Sports racecards page to extract summary data.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    races = []

    # Find all meeting headers
    meeting_headers = soup.select("h3.sdc-site-card-header__title")

    for header in meeting_headers:
        track_name_tag = header.find("a")
        if not track_name_tag:
            continue
        track_name = track_name_tag.text.strip()

        # The race links are in the next sibling div
        card_body = header.find_parent("div", class_="sdc-site-card-header").find_next_sibling("div", class_="sdc-site-card-body")

        if not card_body:
            continue

        race_links = card_body.select("a.sdc-site-racing-race-card__race")
        for i, link in enumerate(race_links):
            race_time_tag = link.select_one("span.sdc-site-racing-race-card__race-time")
            race_time = race_time_tag.text.strip() if race_time_tag else "Unknown"

            runner_count_tag = link.select_one("span.sdc-site-racing-race-card__race-subtitle")
            number_of_runners = None
            if runner_count_tag:
                runner_count_text = runner_count_tag.text.strip()
                runner_count_match = re.search(r"(\d+)", runner_count_text)
                if runner_count_match:
                    number_of_runners = int(runner_count_match.group(1))

            race_name_tag = link.select_one("span.sdc-site-racing-race-card__race-name")
            race_name = race_name_tag.text.strip() if race_name_tag else ""

            race = NormalizedRace(
                race_id=f"{track_name.replace(' ', '')}-{race_time}-{race_name}",
                track_name=track_name,
                race_number=i + 1,
                number_of_runners=number_of_runners,
                race_type='Thoroughbred',
            )
            races.append(race)

    return races


class SkySportsAdapter(BaseAdapterV3):
    """
    Adapter for skysports.com/racing/racecards.
    """
    SOURCE_ID = "skysports"

    def __init__(self, config=None):
        super().__init__(config)
        self.url = "https://www.skysports.com/racing/racecards"

    def fetch(self) -> str:
        """
        This method is a placeholder and should be mocked for tests.
        """
        raise NotImplementedError("This fetch method should be mocked for testing.")

    def parse_races(self, html_content: str) -> list[NormalizedRace]:
        """
        Parses the HTML content to extract race summaries.
        """
        return parse_race_summaries(html_content)
