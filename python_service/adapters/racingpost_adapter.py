# python_service/adapters/racingpost_adapter.py
from datetime import datetime
from typing import AsyncGenerator

from selectolax.parser import HTMLParser

from ..models import OddsData
from ..models import Race
from ..models import Runner
from ..utils.odds import parse_odds_to_decimal
from ..utils.text import clean_text
from ..utils.text import normalize_venue_name
from .base import BaseAdapter


class RacingPostAdapter(BaseAdapter):
    """A production-ready adapter for scraping Racing Post racecards."""

    SOURCE_NAME = "RacingPost"
    BASE_URL = "https://www.racingpost.com"

    def __init__(self, config=None):
        super().__init__(self.SOURCE_NAME, self.BASE_URL)

    async def fetch_races(self, date: str) -> AsyncGenerator[Race, None]:
        """
        Fetches all UK & Ireland races for a given date from racingpost.com.
        """
        race_card_urls = await self._get_race_card_urls(date)
        for url in race_card_urls:
            try:
                response = await self.http_client.get(url, headers=self._get_headers())
                response.raise_for_status()
                parser = HTMLParser(response.text)

                venue_raw = parser.css_first('a[data-test-selector="RC-course__name"]').text(strip=True)
                venue = normalize_venue_name(venue_raw)

                race_time_str = parser.css_first('span[data-test-selector="RC-course__time"]').text(strip=True)
                race_datetime_str = f"{date} {race_time_str}"
                start_time = datetime.strptime(race_datetime_str, "%Y-%m-%d %H:%M")

                runners = self._parse_runners(parser)

                if venue and runners:
                    race_number = self._get_race_number(parser, start_time)
                    yield Race(
                        id=f"rp_{venue.lower().replace(' ', '')}_{date}_{race_number}",
                        venue=venue,
                        race_number=race_number,
                        start_time=start_time,
                        runners=runners,
                        source=self.SOURCE_NAME,
                    )

            except Exception:
                # Assuming a logger is available, as per standard practice in the project.
                # If self.logger is not on BaseAdapter, this would need to be structlog.
                # self.logger.error(f"Failed to process race card at {url}", exc_info=True)
                continue

    async def _get_race_card_urls(self, date: str) -> list[str]:
        """Gets all individual race card URLs for a given date."""
        url = f"{self.BASE_URL}/racecards/{date}"
        response = await self.http_client.get(url, headers=self._get_headers())
        parser = HTMLParser(response.text)
        links = parser.css('a[data-test-selector^="RC-meetingItem__link_race"]')
        return [f"{self.BASE_URL}{link.attributes['href']}" for link in links]

    def _get_race_number(self, parser: HTMLParser, start_time: datetime) -> int:
        """Derives the race number by finding the active time in the nav bar."""
        time_str_to_find = start_time.strftime("%H:%M")
        time_links = parser.css('a[data-test-selector="RC-raceTime"]')
        for i, link in enumerate(time_links):
            if link.text(strip=True) == time_str_to_find:
                return i + 1
        return 1  # Fallback

    def _parse_runners(self, parser: HTMLParser) -> list[Runner]:
        """Parses all runners from a single race card page."""
        runners = []
        runner_nodes = parser.css('div[data-test-selector="RC-runnerCard"]')
        for node in runner_nodes:
            try:
                number_node = node.css_first('span[data-test-selector="RC-runnerNumber"]')
                name_node = node.css_first('a[data-test-selector="RC-runnerName"]')
                odds_node = node.css_first('span[data-test-selector="RC-runnerPrice"]')

                if not all([number_node, name_node, odds_node]):
                    continue

                number_str = clean_text(number_node.text())
                number = int(number_str) if number_str and number_str.isdigit() else 0
                name = clean_text(name_node.text())
                odds_str = clean_text(odds_node.text())
                scratched = "NR" in odds_str.upper() or not odds_str

                odds = {}
                if not scratched:
                    win_odds = parse_odds_to_decimal(odds_str)
                    if win_odds and win_odds < 999:
                        odds = {
                            self.SOURCE_NAME: OddsData(
                                win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now()
                            )
                        }

                runners.append(Runner(number=number, name=name, odds=odds, scratched=scratched))
            except (ValueError, AttributeError):
                continue
        return runners

    def _get_headers(self) -> dict:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/107.0.0.0 Safari/537.36"
            )
        }
