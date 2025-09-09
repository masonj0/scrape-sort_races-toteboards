import math
from typing import List, Dict, Optional

from .config import SCORER_WEIGHTS
from .models import Race, Runner

class RaceScorer:
    """
    Analyzes a Race to produce a score based on a weighted combination of factors.
    The weights for each factor are drawn from config.py to allow for easy tuning.
    """
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initializes the scorer with weights, falling back to the config file."""
        self.weights = weights if weights is not None else SCORER_WEIGHTS

    def _get_sorted_runners(self, race: Race) -> List[Runner]:
        """Returns runners sorted by their odds, lowest first."""
        return sorted(race.runners, key=lambda r: r.odds or float('inf'))

    def _calculate_field_size_score(self, race: Race) -> float:
        """
        Calculates the field size score. A smaller field is generally considered
        less competitive, so we reward it with a higher score (inverse relationship).
        """
        if not race.number_of_runners:
            return 0.0
        return 1 / race.number_of_runners

    def _calculate_favorite_odds_score(self, race: Race, sorted_runners: List[Runner]) -> float:
        """
        Calculates the favorite's odds score. A higher-odds favorite suggests
        a more open race, which can be a valuable signal.
        """
        if not sorted_runners:
            return 0.0
        return sorted_runners[0].odds or 0.0

    def _calculate_contention_score(self, race: Race, sorted_runners: List[Runner]) -> float:
        """
        Calculates the contention score. This measures the gap between the favorite
        and the second favorite. A large gap (low contention) is rewarded with a
        higher score, as it suggests a more predictable race.
        If there's only one runner, we use their odds as the score.
        """
        if len(sorted_runners) < 2:
            return self._calculate_favorite_odds_score(race, sorted_runners)

        fav_odds = sorted_runners[0].odds or 0.0
        second_fav_odds = sorted_runners[1].odds or 0.0
        return abs(second_fav_odds - fav_odds)

    def score(self, race: Race) -> Dict[str, float]:
        """
        Calculates a weighted score for a race based on various factors.
        Returns a dictionary with the total score and the individual factor scores
        for transparency and potential UI display.
        """
        if not race.runners:
            return {"total_score": 0.0, "field_size_score": 0.0, "favorite_odds_score": 0.0, "contention_score": 0.0}

        sorted_runners = self._get_sorted_runners(race)

        # Calculate raw scores for each factor
        field_size_score = self._calculate_field_size_score(race)
        favorite_odds_score = self._calculate_favorite_odds_score(race, sorted_runners)
        contention_score = self._calculate_contention_score(race, sorted_runners)

        # Apply weights from config
        weighted_field_size = field_size_score * self.weights.get("FIELD_SIZE_WEIGHT", 0)
        weighted_favorite_odds = favorite_odds_score * self.weights.get("FAVORITE_ODDS_WEIGHT", 0)
        weighted_contention = contention_score * self.weights.get("CONTENTION_WEIGHT", 0)

        # Calculate the final total score
        total_score = weighted_field_size + weighted_favorite_odds + weighted_contention

        return {
            "total_score": total_score,
            "field_size_score": field_size_score,
            "favorite_odds_score": favorite_odds_score,
            "contention_score": contention_score,
        }

def score_races(races: List[Race]) -> List[Race]:
    """
    A helper function to score a list of races and attach the scoring
    details back to each race object.
    """
    scorer = RaceScorer()
    for race in races:
        scores = scorer.score(race)
        # Attach the detailed dictionary for the UI
        setattr(race, 'scores', scores)
        # Attach the final score for sorting and filtering
        setattr(race, 'score', scores.get('total_score', 0.0))
    return races


def _get_dynamic_odds_thresholds(field_size: int) -> Dict[str, float]:
    """
    Returns the required odds thresholds for the favorite and second-favorite
    based on the number of runners in the race.
    """
    if field_size >= 7:
        return {"fav": 1.0, "second_fav": 4.0}
    if field_size == 6:
        return {"fav": 1.0, "second_fav": 3.5}
    if field_size == 5:
        return {"fav": 0.8, "second_fav": 3.0}
    if field_size == 4:
        return {"fav": 0.5, "second_fav": 2.0}
    return {"fav": 0.0, "second_fav": 0.0}  # Default for very small fields


def find_checkmate_opportunities(races: List[Race]) -> List[Race]:
    """
    Filters a list of races to find those that meet the dynamic "Checkmate" criteria.
    """
    checkmate_races = []
    for race in races:
        if not race.runners or not race.number_of_runners:
            continue

        thresholds = _get_dynamic_odds_thresholds(race.number_of_runners)

        sorted_runners = sorted(race.runners, key=lambda r: r.odds or float('inf'))

        if len(sorted_runners) < 2:
            continue

        favorite_odds = sorted_runners[0].odds or 0.0
        second_favorite_odds = sorted_runners[1].odds or 0.0

        if (
            favorite_odds > thresholds["fav"]
            and second_favorite_odds > thresholds["second_fav"]
        ):
            checkmate_races.append(race)

    return checkmate_races
