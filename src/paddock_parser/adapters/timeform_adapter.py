import logging
from bs4 import BeautifulSoup
from paddock_parser.base import BaseAdapterV3, NormalizedRace
from datetime import datetime
from typing import List

class TimeformAdapter(BaseAdapterV3):
    """
    Adapter for timeform.com.

    This adapter is a 'minimalist' implementation that parses the main racecards
    summary page. It extracts a list of all races for the day but does not
    currently fetch the individual detail page for each race to get runner info.
    """
    SOURCE_ID = "timeform"

    def __init__(self, config=None):
        super().__init__(config)
        logging.getLogger(__name__).setLevel(self.config.get('log_level', logging.INFO))

    async def fetch(self) -> List[NormalizedRace]:
        """This is an offline adapter and should not be fetched by the pipeline."""
        raise NotImplementedError("TimeformAdapter is an offline adapter and does not support live fetching.")

    def parse_races(self, html_content: str) -> list[NormalizedRace]:
        """
        Parses the HTML content of a Timeform race card index page.

        This implementation extracts the basic details for all races listed on the
        summary page. It does not contain runner information as that requires
        fetching individual race pages, which is not supported by the current
        mock data.
        """
        if not html_content:
            logging.warning("HTML content for TimeformAdapter is empty.")
            return []

        soup = BeautifulSoup(html_content, 'lxml')
        races = []

        meeting_blocks = soup.select("div.w-racecard-grid-meeting")
        logging.info(f"Found {len(meeting_blocks)} meeting blocks on the page.")

        for meeting in meeting_blocks:
            track_name_tag = meeting.select_one("h2")
            if not track_name_tag:
                logging.warning("Could not find track name for a meeting block.")
                continue

            track_name = track_name_tag.text.strip()

            race_list_items = meeting.select("ul.w-racecard-grid-meeting-races-compact > li")
            for i, race_item in enumerate(race_list_items):
                time_tag = race_item.select_one("b")
                if not time_tag:
                    logging.warning(f"Could not find time for a race at {track_name}.")
                    continue

                race_time_str = time_tag.text.strip()

                try:
                    # Use today's date for the datetime object
                    post_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
                except ValueError:
                    logging.warning(f"Could not parse time '{race_time_str}' for a race at {track_name}.")
                    post_time = None

                # NOTE: The number of runners is not available on the summary page.
                # A full implementation would require fetching the detail page for each race.
                race = NormalizedRace(
                    race_id=f"{track_name.replace(' ', '')}-{race_time_str}",
                    track_name=track_name,
                    race_number=i + 1,
                    post_time=post_time,
                    runners=[],
                    number_of_runners=0
                )
                races.append(race)

        logging.info(f"Successfully parsed {len(races)} races from Timeform.")
        return races
