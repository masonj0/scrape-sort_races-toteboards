# python_service/adapters/sporting_life_adapter.py

import asyncio
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import httpx
import structlog
from bs4 import BeautifulSoup
from bs4 import Tag

from ..models import OddsData
from ..models import Race
from ..models import Runner
from ..utils.odds import parse_odds_to_decimal
from .base import BaseAdapter

log = structlog.get_logger(__name__)


def _clean_text(text: Optional[str]) -> Optional[str]:
    return " ".join(text.strip().split()) if text else None


class SportingLifeAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(source_name="SportingLife", base_url="https://www.sportinglife.com")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            race_links = await self._get_race_links(http_client)
            tasks = [self._fetch_and_parse_race(link, http_client) for link in race_links]
            races = [race for race in await asyncio.gather(*tasks) if race]
            return self._format_response(races, start_time, is_success=True)
        except Exception as e:
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    async def _get_race_links(self, http_client: httpx.AsyncClient) -> List[str]:
        response_html = await self.make_request(http_client, "GET", "/horse-racing/racecards")
        if not response_html:
            return []
        soup = BeautifulSoup(response_html, "html.parser")
        links = {a["href"] for a in soup.select("a.hr-race-card-meeting__race-link[href]")}
        return [f"{self.base_url}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str, http_client: httpx.AsyncClient) -> Optional[Race]:
        try:
            response_html = await self.make_request(http_client, "GET", url)
            if not response_html:
                return None
            soup = BeautifulSoup(response_html, "html.parser")
            track_name = _clean_text(soup.select_one("a.hr-race-header-course-name__link").get_text())
            race_time_str = _clean_text(soup.select_one("span.hr-race-header-time__time").get_text())
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
            active_link = soup.select_one("a.hr-race-header-navigation-link--active")
            race_number = soup.select("a.hr-race-header-navigation-link").index(active_link) + 1 if active_link else 1
            runners = [self._parse_runner(row) for row in soup.select("div.hr-racing-runner-card")]
            return Race(
                id=f"sl_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}",
                venue=track_name,
                race_number=race_number,
                start_time=start_time,
                runners=[r for r in runners if r],
                source=self.source_name,
            )
        except Exception as e:
            log.error("Error parsing race from SportingLife", url=url, exc_info=e)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("a.hr-racing-runner-horse-name").get_text())
            num_str = _clean_text(row.select_one("span.hr-racing-runner-saddle-cloth-no").get_text())
            number = int("".join(filter(str.isdigit, num_str)))
            odds_str = _clean_text(row.select_one("span.hr-racing-runner-odds").get_text())
            win_odds = parse_odds_to_decimal(odds_str)
            odds_data = (
                {self.source_name: OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())}
                if win_odds and win_odds < 999
                else {}
            )
            return Runner(number=number, name=name, odds=odds_data)
        except Exception as e:
            log.warning("Failed to parse runner from SportingLife", exc_info=e)
            return None
