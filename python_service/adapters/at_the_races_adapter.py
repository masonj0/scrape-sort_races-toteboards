# python_service/adapters/at_the_races_adapter.py

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
from ..utils.text import clean_text
from ..utils.text import normalize_venue_name
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class AtTheRacesAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(source_name="AtTheRaces", base_url="https://www.attheraces.com", config=config)

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            race_links = await self._get_race_links(http_client)
            tasks = [self._fetch_and_parse_race(link, http_client) for link in race_links]
            races = [race for race in await asyncio.gather(*tasks) if race]
            return self._format_response(races, start_time, is_success=True)
        except Exception as e:
            log.error(f"Error fetching races from AtTheRaces: {e}", exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    async def _get_race_links(self, http_client: httpx.AsyncClient) -> List[str]:
        response = await self.make_request(http_client, "GET", "/racecards")
        if not response:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        links = {a["href"] for a in soup.select("a.race-time-link[href]")}
        return [f"{self.base_url}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str, http_client: httpx.AsyncClient) -> Optional[Race]:
        try:
            response = await self.make_request(http_client, "GET", url)
            if response is None:
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            header = soup.select_one("h1.heading-racecard-title").get_text()
            track_name_raw, race_time = [p.strip() for p in header.split("|")[:2]]
            track_name = normalize_venue_name(track_name_raw)
            active_link = soup.select_one("a.race-time-link.active")
            race_number = active_link.find_parent("div", "races").select("a.race-time-link").index(active_link) + 1
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time}", "%Y-%m-%d %H:%M")
            runners = [self._parse_runner(row) for row in soup.select("div.card-horse")]
            return Race(
                id=f"atr_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}",
                venue=track_name,
                race_number=race_number,
                start_time=start_time,
                runners=[r for r in runners if r],
                source=self.source_name,
            )
        except Exception as e:
            log.error("Error parsing race from AtTheRaces", url=url, exc_info=e)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = clean_text(row.select_one("h3.horse-name a").get_text())
            num_str = clean_text(row.select_one("span.horse-number").get_text())
            number = int("".join(filter(str.isdigit, num_str)))
            odds_str = clean_text(row.select_one("button.best-odds").get_text())
            win_odds = parse_odds_to_decimal(odds_str)
            odds_data = (
                {self.source_name: OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())}
                if win_odds and win_odds < 999
                else {}
            )
            return Runner(number=number, name=name, odds=odds_data)
        except Exception as e:
            log.warning("Failed to parse runner", exc_info=e)
            return None
