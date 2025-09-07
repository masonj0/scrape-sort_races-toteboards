from datetime import datetime, timedelta
from typing import List

from .base import NormalizedRace
from .models import Race, Runner

def get_high_roller_races(races: List[Race], now: datetime) -> List[Race]:
    """
    Filters and scores races to find "High Roller" opportunities.
    """
    valid_races = []
    max_time_to_post = timedelta(minutes=25)

    for race in races:
        # 1. Time filtering
        try:
            race_hour, race_minute = map(int, race.race_time.split(':'))
            race_dt = now.replace(hour=race_hour, minute=race_minute, second=0, microsecond=0)
            if race_dt < now - timedelta(hours=1):
                race_dt += timedelta(days=1)
        except (ValueError, TypeError):
            continue

        time_to_post = race_dt - now
        if not (timedelta(minutes=0) < time_to_post <= max_time_to_post):
            continue

        # 2. Runner count filtering (must be less than 7)
        if not (hasattr(race, 'number_of_runners') and race.number_of_runners and 0 < race.number_of_runners < 7):
            continue

        # 3. Scoring based on favorite's odds
        min_odds = float('inf')
        for runner in race.runners:
            odds = runner.odds or float('inf') # Odds are now floats
            if odds < min_odds:
                min_odds = odds

        if min_odds != float('inf'):
            setattr(race, 'high_roller_score', min_odds)
            valid_races.append(race)

    # 4. Sort by the dynamically added score
    valid_races.sort(key=lambda r: getattr(r, 'high_roller_score', float('inf')), reverse=True)
    return valid_races


class RaceScorer:
    """Analyzes a Race to produce a score based on specific criteria."""

    def score(self, race: Race) -> float:
        """Calculates a score for a single race based on the number of runners."""
        if not hasattr(race, 'number_of_runners') or not race.number_of_runners:
            return 0.0
        field_size = race.number_of_runners
        if 5 <= field_size <= 7:
            return 100.0
        if 8 <= field_size <= 10:
            return 80.0
        if 3 <= field_size <= 4:
            return 60.0
        if 11 <= field_size <= 12:
            return 40.0
        return 20.0


def calculate_weighted_score(race: Race, weights: dict) -> float:
    """
    Calculates a weighted score for a race based on various factors.
    """
    if not race.runners or not hasattr(race, 'number_of_runners') or not race.number_of_runners:
        return 0.0

    # Find the favorite (lowest odds)
    favorite_odds = float('inf')
    for runner in race.runners:
        odds = runner.odds or float('inf') # Odds are now floats
        if odds < favorite_odds:
            favorite_odds = odds

    if favorite_odds == float('inf'):
        favorite_odds = 0

    # Calculate score components
    field_size_component = (1 / race.number_of_runners) * weights.get("FIELD_SIZE_WEIGHT", 0)
    favorite_odds_component = favorite_odds * weights.get("FAVORITE_ODDS_WEIGHT", 0)

    # Calculate final score
    score = field_size_component + favorite_odds_component
    return score


def score_trifecta_factors(races: List[Race]) -> dict:
    """
    Categorizes races into three tiers based on the "Trifecta of Factors."
    The base factor is always having fewer than 7 runners.
    """
    tiered_results = {"tier_1": [], "tier_2": [], "tier_3": []}

    for race in races:
        # Base criteria: must have fewer than 7 runners to be considered for any tier.
        if len(race.runners) >= 7:
            continue

        factors_met = 1  # Start with 1 factor for passing the runner count criteria.

        # Sort runners by odds to find favorite and 2nd favorite
        runners_with_odds = sorted([r for r in race.runners if r.odds is not None], key=lambda r: r.odds)

        # Factor 2: Favorite's odds > 1.0
        if len(runners_with_odds) >= 1 and runners_with_odds[0].odds > 1.0:
            factors_met += 1

        # Factor 3: Second favorite's odds > 4.0
        if len(runners_with_odds) >= 2 and runners_with_odds[1].odds > 4.0:
            factors_met += 1

        if factors_met == 3:
            tiered_results["tier_1"].append(race)
        elif factors_met == 2:
            tiered_results["tier_2"].append(race)
        elif factors_met == 1:
            tiered_results["tier_3"].append(race)

    return tiered_results
