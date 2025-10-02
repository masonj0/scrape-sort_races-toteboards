# python_service/engine.py

import time
import logging
import requests
from typing import List, Dict, Any
from .adapters.base import BaseAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.betfair_adapter import BetfairAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .models import FormattedRace, RaceData

class DefensiveFetcher:
    """A more robust fetcher that can handle GET and POST requests."""
    def get(self, url, headers=None):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"GET request to {url} failed: {e}")
            return None

    def post(self, url, headers=None, json=None):
        try:
            response = requests.post(url, headers=headers, json=json, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"POST request to {url} failed: {e}")
            return None

class CheckmateEngine:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fetcher = DefensiveFetcher()
        self.adapters: List[BaseAdapter] = self._load_adapters()
        self._cache: List[RaceData] = []
        self._last_update: float = 0

    def _load_adapters(self) -> List[BaseAdapter]:
        return [
            TVGAdapter(self.fetcher),
            BetfairAdapter(self.fetcher),
            PointsBetAdapter(self.fetcher),
            RacingAndSportsAdapter(self.fetcher),
        ]

    def _needs_refresh(self) -> bool:
        return (time.time() - self._last_update) > 30  # 30-second cache

    def scrape_all(self) -> Dict[str, Any]:
        self.logger.info("Starting scrape cycle...")
        all_races = []
        for adapter in self.adapters:
            try:
                races = adapter.fetch_races()
                all_races.extend(races)
                self.logger.info(f"{adapter.SOURCE_ID} fetched {len(races)} races.")
            except Exception as e:
                self.logger.error(f"Adapter {adapter.SOURCE_ID} failed: {e}")
        self._cache = all_races
        self._last_update = time.time()
        return {"success": True, "races_found": len(all_races)}

    def get_current_odds(self) -> List[FormattedRace]:
        if not self._cache or self._needs_refresh():
            self.scrape_all()
        return self._format_for_frontend()

    def _format_for_frontend(self) -> List[FormattedRace]:
        formatted_races = []
        for race in self._cache:
            formatted_race = FormattedRace(
                race_id=race.race_id,
                track=race.track_name,
                race=race.race_number,
                time=race.post_time.strftime('%H:%M'),
                runners=[{'name': r.name, 'odds': str(r.odds) if r.odds is not None else 'N/A'} for r in race.runners]
            )
            formatted_races.append(formatted_race)
        return formatted_races