from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional
import structlog
from decimal import Decimal

from python_service.models import Race, Runner

log = structlog.get_logger(__name__)

def _get_best_win_odds(runner: Runner) -> Optional[Decimal]:
    """Helper to find the best (lowest) win odds for a runner from any source."""
    if not runner.odds:
        return None

    valid_odds = [
        odds_data.win
        for odds_data in runner.odds.values()
        if odds_data and odds_data.win is not None
    ]

    return min(valid_odds) if valid_odds else None

class BaseAnalyzer(ABC):
    """The abstract interface for all future analyzer plugins."""
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def qualify_races(self, races: List[Race]) -> List[Race]:
        """The core method every analyzer must implement."""
        pass

class TrifectaAnalyzer(BaseAnalyzer):
    """Analyzes races and assigns a qualification score based on the 'Trifecta of Factors'."""
    def __init__(self, max_field_size: int = 10, min_favorite_odds: float = 2.5, min_second_favorite_odds: float = 4.0):
        self.max_field_size = max_field_size
        self.min_favorite_odds = Decimal(str(min_favorite_odds))
        self.min_second_favorite_odds = Decimal(str(min_second_favorite_odds))

    def qualify_races(self, races: List[Race]) -> List[Race]:
        """Filters and scores races, returning a sorted list of qualified opportunities."""
        qualified_races = []
        for race in races:
            score = self._evaluate_race(race)
            if score is not None:
                race.qualification_score = score
                qualified_races.append(race)

        # Sort the qualified races by score, descending
        qualified_races.sort(key=lambda r: r.qualification_score, reverse=True)
        log.info("Qualification and scoring complete", qualified_count=len(qualified_races))
        return qualified_races

    def _evaluate_race(self, race: Race) -> Optional[float]:
        """Evaluates a single race and returns a qualification score if it passes, else None."""
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
        fav_odds_score = min(float(favorite_odds) / 10.0, 1.0)
        sec_fav_odds_score = min(float(second_favorite_odds) / 15.0, 1.0)

        # Weighted average
        odds_score = (fav_odds_score * 0.6) + (sec_fav_odds_score * 0.4)
        final_score = (field_score * 0.3) + (odds_score * 0.7)

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