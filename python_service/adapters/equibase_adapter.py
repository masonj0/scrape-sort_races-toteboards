# python_service/adapters/equibase_adapter.py
from datetime import datetime
from typing import AsyncGenerator

from selectolax.parser import HTMLParser

from ..models import OddsData
from ..models import Race
from ..models import Runner
from ..utils.odds import parse_odds_to_decimal
from ..utils.text import clean_text
from .base import BaseAdapter


class EquibaseAdapter(BaseAdapter):
    """A production-ready adapter for scraping Equibase race entries."""

    SOURCE_NAME = "Equibase"
    BASE_URL = "https://www.equibase.com"

    def __init__(self, config=None):
        super().__init__(self.SOURCE_NAME, self.BASE_URL)

    async def fetch_races(self, date_str: str, http_client) -> AsyncGenerator[Race, None]:
        """
        Fetches all US & Canadian races for a given date from equibase.com.
        """
        entry_urls = await self._get_entry_urls(date_str, http_client)
        for url in entry_urls:
            try:
                response = await http_client.get(url, headers=self._get_headers())
                response.raise_for_status()
                parser = HTMLParser(response.text)
                race_links = parser.css("a.program-race-link")
                for link in race_links:
                    race_url = f"{self.BASE_URL}{link.attributes['href']}"
                    yield await self._parse_race(race_url, date_str, http_client)

            except Exception:
                # self.logger.error(f"Failed to process entry page at {url}", exc_info=True)
                continue

    async def _get_entry_urls(self, date_str: str, http_client) -> list[str]:
        """Gets all individual track entry page URLs for a given date."""
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        url = f"{self.BASE_URL}/entries/Entries.cfm?ELEC_DATE={d.month}/{d.day}/{d.year}&STYLE=EQB"
        response = await http_client.get(url, headers=self._get_headers())
        parser = HTMLParser(response.text)
        links = parser.css("div.track-information a")
        return [
            f"{self.BASE_URL}{link.attributes['href']}"
            for link in links
            if "race=" not in link.attributes.get("href", "")
        ]

    async def _parse_race(self, url: str, date_str: str, http_client) -> Race:
        """Parses a single race card page."""
        response = await http_client.get(url, headers=self._get_headers())
        parser = HTMLParser(response.text)

        venue = clean_text(parser.css_first("div.track-information strong").text())
        race_number = int(parser.css_first("div.race-information strong").text().replace("Race", "").strip())
        post_time_str = parser.css_first("p.post-time span").text().strip()
        start_time = self._parse_post_time(date_str, post_time_str)

        runners = []
        runner_nodes = parser.css("table.entries-table tbody tr")
        for node in runner_nodes:
            try:
                number = int(node.css_first("td:nth-child(1)").text(strip=True))
                name = clean_text(node.css_first("td:nth-child(3)").text())
                odds_str = clean_text(node.css_first("td:nth-child(10)").text())
                scratched = "scratched" in node.attributes.get("class", "").lower()

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

        return Race(
            id=f"eqb_{venue.lower().replace(' ', '')}_{date_str}_{race_number}",
            venue=venue,
            race_number=race_number,
            start_time=start_time,
            runners=runners,
            source=self.SOURCE_NAME,
        )

    def _parse_post_time(self, date_str: str, time_str: str) -> datetime:
        """Parses a time string like 'Post Time: 12:30 PM ET' into a datetime object."""
        time_part = time_str.split(" ")[-2] + " " + time_str.split(" ")[-1]
        dt_str = f"{date_str} {time_part}"
        return datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")

    def _get_headers(self) -> dict:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/107.0.0.0 Safari/537.36"
            )
        }
