from typing import List
import structlog
from decimal import Decimal

from python_service.models import Race

log = structlog.get_logger(__name__)

class TrifectaAnalyzer:
    """Analyzes a list of races to find qualified betting opportunities."""

    def __init__(self, min_runners: int = 8, min_favorite_odds: float = 2.0):
        self.min_runners = min_runners
        self.min_favorite_odds = Decimal(str(min_favorite_odds))
        log.info("TrifectaAnalyzer initialized", min_runners=self.min_runners, min_favorite_odds=self.min_favorite_odds)

    def qualify_races(self, races: List[Race]) -> List[Race]:
        """Filters a list of races based on qualification criteria."""
        qualified_races = []
        if not races:
            return []

        for race in races:
            active_runners = [r for r in race.runners if not r.scratched]

            # Rule 1: Must have at least the minimum number of runners
            if len(active_runners) < self.min_runners:
                continue

            # Rule 2: Favorite's odds must be above a certain threshold.
            # This requires finding the lowest 'win' odds among all runners from any source.
            all_win_odds = []
            for runner in active_runners:
                for odds_data in runner.odds.values():
                    if odds_data and odds_data.win is not None:
                        all_win_odds.append(odds_data.win)

            if not all_win_odds:
                # Cannot qualify a race with no available odds.
                continue

            favorite_odds = min(all_win_odds)
            if favorite_odds < self.min_favorite_odds:
                continue

            qualified_races.append(race)

        log.info("Race qualification complete", total_races=len(races), qualified_races=len(qualified_races))
        return qualified_races