# python_service/engine.py
# The refactored, supercharged version of the Python Collection Service engine.

import logging
import concurrent.futures
import time
import json
from typing import List
from pydantic_settings import BaseSettings

# Import the new, modular components
from .adapters.base import Race, DefensiveFetcher
from .adapters import TVGAdapter, BetfairExchangeAdapter, PointsBetAdapter

# --- Finalized Settings Model ---
# This remains here as it's the central configuration for the service.
class Settings(BaseSettings):
    QUALIFICATION_SCORE: float = 75.0
    FIELD_SIZE_OPTIMAL_MIN: int = 4
    FIELD_SIZE_OPTIMAL_MAX: int = 6
    FIELD_SIZE_ACCEPTABLE_MIN: int = 7
    FIELD_SIZE_ACCEPTABLE_MAX: int = 8
    FIELD_SIZE_OPTIMAL_POINTS: int = 30
    FIELD_SIZE_ACCEPTABLE_POINTS: int = 10
    FIELD_SIZE_PENALTY_POINTS: int = -20
    FAV_ODDS_POINTS: int = 30
    MAX_FAV_ODDS: float = 3.5
    SECOND_FAV_ODDS_POINTS: int = 40
    MIN_2ND_FAV_ODDS: float = 4.0
    DATABASE_BATCH_SIZE: int = 100
    RUST_ENGINE_TIMEOUT: int = 10
    ODDS_API_KEY: str = ""

# A list of the production-ready, refactored adapter classes.
PRODUCTION_ADAPTERS = [
    TVGAdapter,
    BetfairExchangeAdapter,
    PointsBetAdapter
]

# --- Supercharged Orchestrator ---
class SuperchargedOrchestrator:
    """
    The orchestrator is responsible for managing all adapters, fetching data
    concurrently, and returning standardized results along with status reports.
    """
    def __init__(self, settings: Settings):
        self.fetcher = DefensiveFetcher()
        self.settings = settings
        # Instantiate each adapter class from our production list
        self.adapters = [Adapter(self.fetcher) for Adapter in PRODUCTION_ADAPTERS]
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_races_parallel(self) -> tuple[list[Race], list[dict]]:
        """
        Executes all adapters in parallel and aggregates their results.
        """
        all_races, statuses = [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): adapter for adapter in self.adapters}
            for future in concurrent.futures.as_completed(future_to_adapter):
                adapter = future_to_adapter[future]
                adapter_id = adapter.SOURCE_ID
                start_time = time.time()
                status = {"adapter_id": adapter_id, "timestamp": time.time(), "status": "ERROR", "races_found": 0, "error_message": "Unknown error", "response_time": 0}
                try:
                    races = future.result()
                    all_races.extend(races)
                    end_time = time.time()
                    status.update({"status": "OK", "races_found": len(races), "error_message": None, "response_time": end_time - start_time})
                    statuses.append(status)
                except Exception as e:
                    end_time = time.time()
                    self.logger.error(f"Adapter {adapter_id} failed: {e}", exc_info=True)
                    status.update({"error_message": str(e), "response_time": end_time - start_time})
                    statuses.append(status)

        self.logger.info(f"Orchestrator fetched a total of {len(all_races)} races from {len(self.adapters)} adapters.")
        return all_races, statuses

# --- Enhanced Trifecta Analyzer ---
class EnhancedTrifectaAnalyzer:
    """
    Analyzes a race to produce a Checkmate Score based on various factors.
    """
    def __init__(self, settings: Settings):
        self.settings = settings

    def analyze_race_advanced(self, race: Race) -> Race:
        """
        Calculates a score for a single race based on field size and odds.
        """
        score = 0.0
        trifecta_factors = {}

        # Filter for runners that have valid odds for analysis
        horses_with_odds = sorted([r for r in race.runners if r.odds is not None and r.odds < 999.0], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)

        # Field Size Factor
        if self.settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= self.settings.FIELD_SIZE_OPTIMAL_MAX:
            points, ok, reason = self.settings.FIELD_SIZE_OPTIMAL_POINTS, True, f"Optimal field size ({num_runners})"
        elif self.settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= self.settings.FIELD_SIZE_ACCEPTABLE_MAX:
            points, ok, reason = self.settings.FIELD_SIZE_ACCEPTABLE_POINTS, True, f"Acceptable field size ({num_runners})"
        else:
            points, ok, reason = self.settings.FIELD_SIZE_PENALTY_POINTS, False, f"Field size not ideal ({num_runners})"
        score += points
        trifecta_factors["fieldSize"] = {"points": points, "ok": ok, "reason": reason}

        # Odds Factors (only if there are enough runners)
        if num_runners >= 2:
            fav, sec_fav = horses_with_odds[0], horses_with_odds[1]

            # Favorite Odds Factor
            if fav.odds <= self.settings.MAX_FAV_ODDS:
                points, ok, reason = self.settings.FAV_ODDS_POINTS, True, f"Favorite odds OK ({fav.odds:.2f})"
            else:
                points, ok, reason = 0, False, f"Favorite odds too high ({fav.odds:.2f})"
            score += points
            trifecta_factors["favoriteOdds"] = {"points": points, "ok": ok, "reason": reason}

            # Second Favorite Odds Factor
            if sec_fav.odds >= self.settings.MIN_2ND_FAV_ODDS:
                points, ok, reason = self.settings.SECOND_FAV_ODDS_POINTS, True, f"2nd Favorite OK ({sec_fav.odds:.2f})"
            else:
                points, ok, reason = 0, False, f"2nd Favorite odds too low ({sec_fav.odds:.2f})"
            score += points
            trifecta_factors["secondFavoriteOdds"] = {"points": points, "ok": ok, "reason": reason}

        race.checkmate_score = score
        race.is_qualified = score >= self.settings.QUALIFICATION_SCORE
        race.trifecta_factors_json = json.dumps(trifecta_factors)

        return race