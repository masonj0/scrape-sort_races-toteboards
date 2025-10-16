# python_service/adapters/timeform_adapter.py

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


class TimeformAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(source_name="Timeform", base_url="https://www.timeform.com", config=config)

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
        response = await self.make_request(http_client, "GET", "/horse-racing/racecards")
        if not response:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        links = {a["href"] for a in soup.select("a.rp-racecard-off-link[href]")}
        return [f"{self.base_url}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str, http_client: httpx.AsyncClient) -> Optional[Race]:
        try:
            response = await self.make_request(http_client, "GET", url)
            if not response:
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            track_name = _clean_text(soup.select_one("h1.rp-raceTimeCourseName_name").get_text())
            race_time_str = _clean_text(soup.select_one("span.rp-raceTimeCourseName_time").get_text())
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
            all_times = [_clean_text(a.get_text()) for a in soup.select("a.rp-racecard-off-link")]
            race_number = all_times.index(race_time_str) + 1 if race_time_str in all_times else 1
            runners = [self._parse_runner(row) for row in soup.select("div.rp-horseTable_mainRow")]
            return Race(
                id=f"tf_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}",
                venue=track_name,
                race_number=race_number,
                start_time=start_time,
                runners=[r for r in runners if r],
                source=self.source_name,
            )
        except Exception as e:
            log.error("Error parsing race from Timeform", url=url, exc_info=e)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("a.rp-horseTable_horse-name").get_text())
            num_str = _clean_text(row.select_one("span.rp-horseTable_horse-number").get_text()).strip("()")
            number = int("".join(filter(str.isdigit, num_str)))
            odds_str = _clean_text(row.select_one("button.rp-bet-placer-btn__odds").get_text())
            win_odds = parse_odds_to_decimal(odds_str)
            odds_data = (
                {self.source_name: OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())}
                if win_odds and win_odds < 999
                else {}
            )
            return Runner(number=number, name=name, odds=odds_data)
        except Exception as e:
            log.warning("Failed to parse runner from Timeform", exc_info=e)
            return None

    def _format_response(
        self, races: List[Race], start_time: datetime, is_success: bool, error_message: str = None
    ) -> Dict[str, Any]:
        return {
            "races": races,
            "source_info": {
                "name": self.source_name,
                "status": "SUCCESS" if is_success else "FAILED",
                "races_fetched": len(races),
                "error_message": error_message,
                "fetch_duration": (datetime.now() - start_time).total_seconds(),
            },
        }
