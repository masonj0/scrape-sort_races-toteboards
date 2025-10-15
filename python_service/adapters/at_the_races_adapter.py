# python_service/adapters/at_the_races_adapter.py
from datetime import datetime
from typing import Any, List, Optional

from selectolax.parser import HTMLParser, Node

from ..models import Race, Runner
from ..utils.text import normalize_venue_name, clean_text
from .base_v3 import BaseAdapterV3 # Inherit from the new base class

class AtTheRacesAdapter(BaseAdapterV3):
    """Adapter for scraping attheraces.com, refactored to use BaseAdapterV3."""

    SOURCE_NAME = "AtTheRaces"
    BASE_URL = "https://www.attheraces.com"

    def __init__(self, **kwargs):
        super().__init__(source_name=self.SOURCE_NAME, base_url=self.BASE_URL)

    async def _fetch_data(self, date: str) -> Any:
        """Fetches the main racecards page HTML for the given date."""
        url = f"{self.BASE_URL}/racecards/{date}"
        response = await self.http_client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.text

    def _parse_races(self, raw_data: Any) -> List[Race]:
        """Parses the raw HTML to extract a list of Race objects."""
        parser = HTMLParser(raw_data)
        races = []
        race_card_nodes = parser.css('div.racecard')

        for card_node in race_card_nodes:
            try:
                venue_raw = self._get_text(card_node, 'h2.racecard-title__course-name')
                if not venue_raw:
                    continue
                venue = normalize_venue_name(venue_raw)

                race_time_str = self._get_text(card_node, 'span.racecard-title__time')
                if not race_time_str:
                    continue

                start_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
                race_number = int(self._get_text(card_node, 'span.racecard-title__race-number').replace('Race', '').strip())
                runners = self._parse_runners(card_node)

                if runners:
                    race = Race(
                        id=f"atr_{venue.lower().replace(' ', '')}_{start_time.strftime('%Y%m%d')}_{race_number}",
                        venue=venue,
                        race_number=race_number,
                        start_time=start_time,
                        runners=runners,
                        source=self.SOURCE_NAME
                    )
                    races.append(race)
            except Exception:
                self.logger.warning("Failed to parse a race card on AtTheRaces.", exc_info=True)
                continue
        return races

    def _parse_runners(self, card_node: Node) -> List[Runner]:
        runners = []
        runner_nodes = card_node.css('div.racecard-runner')
        for runner_node in runner_nodes:
            try:
                number_str = self._get_text(runner_node, 'span.racecard-runner__saddle-cloth-number')
                number = int(number_str) if number_str and number_str.isdigit() else 0

                name = clean_text(self._get_text(runner_node, 'span.racecard-runner__horse-name'))
                odds = clean_text(self._get_text(runner_node, 'span.odds-decimal'))

                if not name or not number:
                    continue

                runners.append(Runner(number=number, name=name, odds=odds, scratched=False if odds else True))
            except (ValueError, AttributeError):
                continue
        return runners

    def _get_text(self, node: Node, selector: str) -> Optional[str]:
        element = node.css_first(selector)
        return element.text(strip=True) if element else None

    def _get_headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }