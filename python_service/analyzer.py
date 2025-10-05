from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional
import structlog
from decimal import Decimal

from python_service.models import Race, Runner

log = structlog.get_logger(__name__)

# --- Corrected Helper Function ---
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


# --- 1. The Abstract Base Class (The Interface) ---
class BaseAnalyzer(ABC):
    """The abstract interface for all future analyzer plugins."""
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def qualify_races(self, races: List[Race]) -> List[Race]:
        """The core method every analyzer must implement."""
        pass


# --- 2. The Concrete Implementation (The First Plugin) ---
class TrifectaAnalyzer(BaseAnalyzer):
    """Analyzes races to find opportunities based on the 'Trifecta of Factors'."""
    def __init__(self, max_field_size: int = 10, min_favorite_odds: float = 2.5, min_second_favorite_odds: float = 4.0):
        self.max_field_size = max_field_size
        self.min_favorite_odds = Decimal(str(min_favorite_odds))
        self.min_second_favorite_odds = Decimal(str(min_second_favorite_odds))
        log.info(
            "TrifectaAnalyzer initialized with TRUE TRIFECTA logic",
            max_field_size=self.max_field_size,
            min_favorite_odds=self.min_favorite_odds,
            min_second_favorite_odds=self.min_second_favorite_odds
        )

    def qualify_races(self, races: List[Race]) -> List[Race]:
        """Filters a list of races based on the true handicapping criteria."""
        qualified_races = []
        for race in races:
            active_runners = [r for r in race.runners if not r.scratched]

            # FACTOR 2: Field size, the lower the better
            if len(active_runners) > self.max_field_size:
                log.debug(f"Race {race.id} disqualified: Field size too large ({len(active_runners)} > {self.max_field_size}).")
                continue

            runners_with_odds = []
            for runner in active_runners:
                best_odds = _get_best_win_odds(runner)
                if best_odds is not None:
                    runners_with_odds.append((runner, best_odds))

            if len(runners_with_odds) < 2:
                log.debug(f"Race {race.id} disqualified: Not enough runners with odds.")
                continue

            # Sort runners by their best odds
            runners_with_odds.sort(key=lambda x: x[1])

            favorite_odds = runners_with_odds[0][1]
            second_favorite_odds = runners_with_odds[1][1]

            # FACTOR 3: Odds for the favorite horse cannot be 'chalky'
            if favorite_odds < self.min_favorite_odds:
                log.debug(f"Race {race.id} disqualified: Favorite odds too low ({favorite_odds} < {self.min_favorite_odds}).")
                continue

            # FACTOR 1: Second-favorite odds, the higher the better
            if second_favorite_odds < self.min_second_favorite_odds:
                log.debug(f"Race {race.id} disqualified: Second favorite odds too low ({second_favorite_odds} < {self.min_second_favorite_odds}).")
                continue

            qualified_races.append(race)

        log.info("True Trifecta qualification complete", total_races=len(races), qualified_races=len(qualified_races))
        return qualified_races


# --- 3. The Orchestrator (The Engine) ---
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
