from datetime import datetime, timedelta
from typing import List

from .models import Race, Runner

def _convert_odds_to_float(odds_str: str) -> float:
    """Converts odds string to a float. Handles 'EVS' and fractions."""
    if isinstance(odds_str, str):
        odds_str = odds_str.strip().upper()
        if odds_str == 'EVS':
            return 1.0
        if '/' in odds_str:
            try:
                num, den = map(int, odds_str.split('/'))
                return num / den
            except (ValueError, ZeroDivisionError):
                return float('inf')
    return float('inf')

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
        except ValueError:
            continue

        time_to_post = race_dt - now
        if not (timedelta(minutes=0) < time_to_post <= max_time_to_post):
            continue

        # 2. Runner count filtering (must be less than 7)
        if not (0 < len(race.runners) < 7):
            continue

        # 3. Scoring based on favorite's odds
        min_odds = float('inf')
        for runner in race.runners:
            odds = _convert_odds_to_float(runner.odds)
            if odds < min_odds:
                min_odds = odds

        if min_odds != float('inf'):
            # The test expects a 'high_roller_score' attribute for sorting.
            # We add it dynamically to the model instance.
            setattr(race, 'high_roller_score', min_odds)
            valid_races.append(race)

    # 4. Sort by the dynamically added score
    valid_races.sort(key=lambda r: r.high_roller_score, reverse=True)

    return valid_races
