from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Any
import structlog
from decimal import Decimal

from python_service.models import Race, Runner

try:
    from win10toast_py3 import ToastNotifier
except (ImportError, RuntimeError):
    ToastNotifier = None

log = structlog.get_logger(__name__)

def _get_best_win_odds(runner: Runner) -> Optional[Decimal]:
    """Gets the best win odds for a runner, filtering out invalid or placeholder values."""
    if not runner.odds:
        return None

    # Filter out invalid or placeholder odds (e.g., > 999)
    valid_odds = [o.win for o in runner.odds.values()
                  if o.win is not None and o.win > 0 and o.win < 999]

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
        self.notifier = RaceNotifier()

    def qualify_races(self, races: List[Race]) -> Dict[str, Any]:
        """Scores all races and returns a dictionary with criteria and a sorted list."""
        scored_races = []
        for race in races:
            # The _evaluate_race method now always returns a float score.
            race.qualification_score = self._evaluate_race(race)
            scored_races.append(race)

        scored_races.sort(key=lambda r: r.qualification_score, reverse=True)

        criteria = {
            "max_field_size": self.max_field_size,
            "min_favorite_odds": float(self.min_favorite_odds),
            "min_second_favorite_odds": float(self.min_second_favorite_odds)
        }

        log.info("Universal scoring complete", total_races_scored=len(scored_races), criteria=criteria)

        for race in scored_races:
            if race.qualification_score and race.qualification_score >= 85:
                self.notifier.notify_qualified_race(race)

        return {"criteria": criteria, "races": scored_races}

    def _evaluate_race(self, race: Race) -> float:
        """Evaluates a single race and returns a qualification score."""
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

        if len(runners_with_odds) < 2:
            return 0.0

        runners_with_odds.sort(key=lambda x: x[1])
        favorite_odds = runners_with_odds[0][1]
        second_favorite_odds = runners_with_odds[1][1]

        # --- Calculate Qualification Score (as inspired by the TypeScript Genesis) ---
        field_score = (self.max_field_size - len(active_runners)) / self.max_field_size

        # Normalize odds scores - cap influence of extremely high odds
        fav_odds_score = min(float(favorite_odds) / FAV_ODDS_NORMALIZATION, 1.0)
        sec_fav_odds_score = min(float(second_favorite_odds) / SEC_FAV_ODDS_NORMALIZATION, 1.0)

        # Weighted average
        odds_score = (fav_odds_score * FAV_ODDS_WEIGHT) + (sec_fav_odds_score * SEC_FAV_ODDS_WEIGHT)
        final_score = (field_score * FIELD_SIZE_SCORE_WEIGHT) + (odds_score * ODDS_SCORE_WEIGHT)

        # --- Apply a penalty if hard filters are not met, instead of returning None ---
        if (len(active_runners) > self.max_field_size or
            favorite_odds < self.min_favorite_odds or
            second_favorite_odds < self.min_second_favorite_odds):
            # Assign a score of 0 to races that would have been filtered out
            return 0.0

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
        return analyzer_class(**kwargs)\n\nclass RaceNotifier:\n    def __init__(self):\n        self.toaster = ToastNotifier() if ToastNotifier else None\n        self.notified_races = set()\n\n    def notify_qualified_race(self, race):\n        if not self.toaster or race.id in self.notified_races:\n            return\n\n        title = f"🏇 High-Value Opportunity!"\n        message = f"""{race.venue} - Race {race.race_number}\nScore: {race.qualification_score:.0f}%\nPost Time: {race.start_time.strftime('%I:%M %p')}"""\n        \n        try:\n            self.toaster.show_toast(title, message, duration=10, threaded=True)\n            self.notified_races.add(race.id)\n            log.info("Notification sent for high-value race", race_id=race.id)\n        except Exception as e:\n            log.error("Failed to send notification", error=str(e), exc_info=True)\n
