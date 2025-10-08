# python_service/adapters/at_the_races_adapter.py

import asyncio
import structlog
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag
from decimal import Decimal, InvalidOperation

from .base import BaseAdapter
from ..models import Race, Runner, OddsData
from .utils import parse_odds

log = structlog.get_logger(__name__)

def _clean_text(text: Optional[str]) -> Optional[str]:
    if text is None: return None
    return ' '.join(text.strip().split())

class AtTheRacesAdapter(BaseAdapter):
    """Adapter for scraping race data from attheraces.com."""

    def __init__(self, config):
        super().__init__(
            source_name="AtTheRaces",
            base_url="https://www.attheraces.com"
        )

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            race_links = await self._get_race_links(http_client)
            tasks = [self._fetch_and_parse_race(link, http_client) for link in race_links]
            races = [race for race in await asyncio.gather(*tasks) if race]
            return self._format_response(races, start_time, is_success=True)
        except Exception as e:
            log.error("AtTheRacesAdapter: Failed to fetch races", error=str(e), exc_info=True)
            return self._format_response([], start_time, is_success=False, error_message=str(e))

    async def _get_race_links(self, http_client: httpx.AsyncClient) -> List[str]:
        url = f"{self.base_url}/racecards"
        response_json = await self.make_request(http_client, 'GET', url)
        soup = BeautifulSoup(response_json, "html.parser")
        links = {a['href'] for a in soup.select("a.race-time-link[href]")}
        return [f"{self.base_url}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str, http_client: httpx.AsyncClient) -> Optional[Race]:
        try:
            response_json = await self.make_request(http_client, 'GET', url)
            soup = BeautifulSoup(response_json, "html.parser")

            header_text = _clean_text(soup.select_one("h1.heading-racecard-title").get_text()).split("|")
            track_name, race_time = [p.strip() for p in header_text[:2]]

            active_link = soup.select_one("a.race-time-link.active")
            all_links_container = active_link.find_parent("div", "races")
            all_links = all_links_container.select("a.race-time-link")
            race_number = all_links.index(active_link) + 1

            runners = [self._parse_runner(row) for row in soup.select("div.card-horse")]

            return Race(
                id=f"atr_{track_name.replace(' ', '')}_{datetime.now().strftime('%Y%m%d')}_R{race_number}",
                venue=track_name,
                race_number=race_number,
                start_time=datetime.strptime(f"{datetime.now().date()} {race_time}", "%Y-%m-%d %H:%M"),
                runners=[r for r in runners if r],
                source=self.source_name
            )
        except Exception as e:
            log.error("AtTheRacesAdapter: Failed to parse race page", url=url, error=str(e), exc_info=True)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("h3.horse-name a").get_text())
            num_str = _clean_text(row.select_one("span.horse-number").get_text())
            number = int(''.join(filter(str.isdigit, num_str)))

            odds_str = _clean_text(row.select_one("button.best-odds").get_text())
            win_odds = Decimal(str(parse_odds(odds_str))) if odds_str else None

            odds_data = {}
            if win_odds and win_odds < 999:
                odds_data[self.source_name] = OddsData(win=win_odds, source=self.source_name, last_updated=datetime.now())

            return Runner(number=number, name=name, odds=odds_data)
        except (AttributeError, ValueError, IndexError):
            return None

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': (datetime.now() - start_time).total_seconds()
            }
        }