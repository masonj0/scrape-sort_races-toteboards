from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Any
import structlog
from decimal import Decimal

from python_service.models import Race, Runner

log = structlog.get_logger(__name__)

def _get_best_win_odds(runner: Runner) -> Optional[Decimal]:
    """Gets the best win odds for a runner, filtering out invalid or placeholder values."""
    if not runner.odds:
        return None

    # Filter out invalid or placeholder odds (e.g., > 999)
    valid_odds = [o.win for o in runner.odds.values() if o.win is not None and o.win < 999]

    if not valid_odds:
        return None

    return min(valid_odds)

class BaseAnalyzer(ABC):
    """The abstract interface for all future analyzer plugins."""
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def qualify_races(self, races: List[Race]) -> Dict[str, Any]:
        """The core method every analyzer must implement."""
        pass

class TrifectaAnalyzer(BaseAnalyzer):
    """Analyzes races and assigns a qualification score based on the 'Trifecta of Factors'."""
    def __init__(self, max_field_size: int = 10, min_favorite_odds: float = 2.5, min_second_favorite_odds: float = 4.0):
        self.max_field_size = max_field_size
        self.min_favorite_odds = Decimal(str(min_favorite_odds))
        self.min_second_favorite_odds = Decimal(str(min_second_favorite_odds))

    def qualify_races(self, races: List[Race]) -> Dict[str, Any]:
        """Filters and scores races, returning a dictionary with criteria and a sorted list of qualified races."""
        qualified_races = []
        for race in races:
            score = self._evaluate_race(race)
            if score is not None:
                race.qualification_score = score
                qualified_races.append(race)

        qualified_races.sort(key=lambda r: r.qualification_score, reverse=True)

        criteria = {
            "max_field_size": self.max_field_size,
            "min_favorite_odds": float(self.min_favorite_odds),
            "min_second_favorite_odds": float(self.min_second_favorite_odds)
        }

        log.info("Qualification and scoring complete", qualified_count=len(qualified_races), criteria=criteria)
        return {"criteria": criteria, "races": qualified_races}

    def _evaluate_race(self, race: Race) -> Optional[float]:
        """Evaluates a single race and returns a qualification score if it passes, else None."""
        # --- Constants for Scoring Logic ---
        FAV_ODDS_NORMALIZATION = 10.0
        SEC_FAV_ODDS_NORMALIZATION = 15.0
        FAV_ODDS_WEIGHT = 0.6
        SEC_FAV_ODDS_WEIGHT = 0.4
        FIELD_SIZE_SCORE_WEIGHT = 0.3
        ODDS_SCORE_WEIGHT = 0.7

        active_runners = [r for r in race.runners if not r.scratched]

        runners_with_odds = []
        for runner in active_runners:
            best_odds = _get_best_win_odds(runner)
            if best_odds is not None:
                runners_with_odds.append((runner, best_odds))

        if len(runners_with_odds) < 2: return None

        runners_with_odds.sort(key=lambda x: x[1])
        favorite_odds = runners_with_odds[0][1]
        second_favorite_odds = runners_with_odds[1][1]

        # --- Apply the Trifecta of Factors as hard filters ---
        if len(active_runners) > self.max_field_size: return None
        if favorite_odds < self.min_favorite_odds: return None
        if second_favorite_odds < self.min_second_favorite_odds: return None

        # --- Calculate Qualification Score (as inspired by the TypeScript Genesis) ---
        field_score = (self.max_field_size - len(active_runners)) / self.max_field_size

        # Normalize odds scores - cap influence of extremely high odds
        fav_odds_score = min(float(favorite_odds) / FAV_ODDS_NORMALIZATION, 1.0)
        sec_fav_odds_score = min(float(second_favorite_odds) / SEC_FAV_ODDS_NORMALIZATION, 1.0)

        # Weighted average
        odds_score = (fav_odds_score * FAV_ODDS_WEIGHT) + (sec_fav_odds_score * SEC_FAV_ODDS_WEIGHT)
        final_score = (field_score * FIELD_SIZE_SCORE_WEIGHT) + (odds_score * ODDS_SCORE_WEIGHT)

        return round(final_score * 100, 2)

class AnalyzerEngine:
    """Discovers and manages all available analyzer plugins."""
    def __init__(self):
        self.analyzers: Dict[str, Type[BaseAnalyzer]] = {}
        self._discover_analyzers()

    def _discover_analyzers(self):
        # In a real plugin system, this would inspect a folder.
        # For now, we register them manually.
        self.register_analyzer('trifecta', TrifectaAnalyzer)
        log.info("AnalyzerEngine discovered plugins", available_analyzers=list(self.analyzers.keys()))

    def register_analyzer(self, name: str, analyzer_class: Type[BaseAnalyzer]):
        self.analyzers[name] = analyzer_class

    def get_analyzer(self, name: str, **kwargs) -> BaseAnalyzer:
        analyzer_class = self.analyzers.get(name)
        if not analyzer_class:
            log.error("Requested analyzer not found", requested_analyzer=name)
            raise ValueError(f"Analyzer '{name}' not found.")
        return analyzer_class(**kwargs)