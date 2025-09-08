import math
from typing import List, Dict, Optional

from .config import SCORER_WEIGHTS
from .models import Race, Runner


class RaceScorer:
    """
    Analyzes a Race to produce a score based on a weighted combination of factors.
    """
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights if weights is not None else SCORER_WEIGHTS

    def _get_sorted_runners(self, race: Race) -> List[Runner]:
        """Returns runners sorted by their odds."""
        return sorted(race.runners, key=lambda r: r.odds or float('inf'))

    def _calculate_field_size_score(self, race: Race) -> float:
        """
        Calculates the field size score. Inverse of the number of runners.
        """
        if not race.number_of_runners:
            return 0.0
        return 1 / race.number_of_runners

    def _calculate_favorite_odds_score(self, race: Race, sorted_runners: List[Runner]) -> float:
        """
        Calculates the favorite odds score. This is simply the odds of the favorite.
        """
        if not sorted_runners:
            return 0.0
        return sorted_runners[0].odds or 0.0

    def _calculate_contention_score(self, race: Race, sorted_runners: List[Runner]) -> float:
        """
        Calculates the contention score.
        - The absolute difference between the odds of the first and second favorites.
        - If there is only one runner, it's the favorite's odds.
        """
        if len(sorted_runners) < 2:
            return self._calculate_favorite_odds_score(race, sorted_runners)

        fav_odds = sorted_runners[0].odds or 0.0
        second_fav_odds = sorted_runners[1].odds or 0.0
        return abs(second_fav_odds - fav_odds)

    def score(self, race: Race) -> Dict[str, float]:
        """
        Calculates a weighted score for a race based on various factors.
        Returns a dictionary with the total score and the individual factor scores.
        """
        if not race.runners:
            return {"total_score": 0.0, "field_size_score": 0.0, "favorite_odds_score": 0.0, "contention_score": 0.0}

        sorted_runners = self._get_sorted_runners(race)

        # Calculate raw scores
        field_size_score = self._calculate_field_size_score(race)
        favorite_odds_score = self._calculate_favorite_odds_score(race, sorted_runners)
        contention_score = self._calculate_contention_score(race, sorted_runners)

        # Calculate weighted scores
        weighted_field_size = field_size_score * self.weights.get("FIELD_SIZE_WEIGHT", 0)
        weighted_favorite_odds = favorite_odds_score * self.weights.get("FAVORITE_ODDS_WEIGHT", 0)
        weighted_contention = contention_score * self.weights.get("CONTENTION_WEIGHT", 0)

        # Total Score
        total_score = weighted_field_size + weighted_favorite_odds + weighted_contention

        return {
            "total_score": total_score,
            "field_size_score": field_size_score,
            "favorite_odds_score": favorite_odds_score,
            "contention_score": contention_score,
        }

def score_races(races: List[Race]) -> List[Race]:
    """Scores a list of races and attaches the score to each race object."""
    scorer = RaceScorer() # Now uses weights from config by default
    for race in races:
        scores = scorer.score(race)
        # Attach the detailed dictionary and the final score to the race object
        setattr(race, 'scores', scores)
        setattr(race, 'score', scores['total_score'])
    return races
