"""
Checkmate V7: `logic.py` - THE BRAIN
"""
from typing import Dict

def quantitative_scoring(race_data: Dict) -> float:
    """Placeholder for quantitative scoring logic."""
    return 7.5

def qualitative_analysis_mock(race_data: Dict) -> Dict:
    """Placeholder for qualitative analysis (LLM call)."""
    return {"probability_multiplier": 1.0}

def apply_final_qualification(score: float, odds: float) -> bool:
    """Placeholder for final qualification logic."""
    return score > 7.0

def get_test_data():
    """Generates a diverse set of test data for development and testing."""
    from .models import Race, Runner
    return [
        # Thoroughbreds
        Race(discipline='Thoroughbred', track='Santa Anita', race_number=1, race_time='1:00 PM', runners=[Runner(name='Star Racer', odds=2.5), Runner(name='Gallop King', odds=3.0)]),
        Race(discipline='Thoroughbred', track='Churchill Downs', race_number=4, race_time='2:30 PM', runners=[Runner(name='Mint Julep', odds=1.8), Runner(name='Derby Dreamer', odds=4.5)]),
        # Greyhounds
        Race(discipline='Greyhound', track='Southland', race_number=8, race_time='7:00 PM', runners=[Runner(name='Rapid Fire', odds=3.0), Runner(name='Silver Bullet', odds=2.0)]),
        Race(discipline='Greyhound', track='Wheeling Island', race_number=10, race_time='8:15 PM', runners=[Runner(name='Box 1 Blitz', odds=4.0), Runner(name='Trap 6 Titan', odds=1.5)]),
        # Harness
        Race(discipline='Harness', track='Meadowlands', race_number=5, race_time='9:00 PM', runners=[Runner(name='Pacing Power', odds=2.2), Runner(name='Trotter Triumphant', odds=3.5)])
    ]

from typing import List, Dict, Optional
from .models import RaceDataSchema, HorseSchema

class TrifectaAnalyzer:
    """
    Implements the 'elegant simplicity' model for identifying Checkmate opportunities.
    """

    def analyze_race(self, race: RaceDataSchema) -> Dict:
        """
        Analyzes a single race based on the "Trifecta of Factors" logic.
        """
        if not race.horses or len(race.horses) < 2:
            return {"qualified": False, "score": 0, "trifectaFactors": {}}

        # Sort horses by odds to find favorite and second favorite
        sorted_horses = sorted(race.horses, key=lambda h: h.odds if h.odds is not None else float('inf'))

        favorite = sorted_horses[0]
        second_favorite = sorted_horses[1]

        # 1. Field Size Factor
        field_size_ok = len(race.horses) < 7

        # 2. Second-Favorite's Odds Factor (2/1 to 8/1)
        # Decimal odds are fractional + 1. So 2/1 is 3.0, 8/1 is 9.0.
        second_favorite_odds_in_range = 3.0 <= second_favorite.odds <= 9.0 if second_favorite.odds else False

        # 3. Favorite's Odds Factor (> 1/2)
        # Decimal odds > 1.5
        favorite_odds_ok = favorite.odds > 1.5 if favorite.odds else False

        # 4. (Optional) Race Class Factor
        is_stakes_or_trial = "Stakes" in race.conditions or "Trial" in race.conditions

        # Qualification Logic
        qualified = all([field_size_ok, second_favorite_odds_in_range, favorite_odds_ok])

        # Scoring Logic (simple for now)
        score = 0
        if field_size_ok: score += 1
        if second_favorite_odds_in_range: score += 1
        if favorite_odds_ok: score += 1
        if is_stakes_or_trial: score += 1

        return {
            "qualified": qualified,
            "score": score,
            "trifectaFactors": {
                "fieldSizeOK": field_size_ok,
                "secondFavoriteOddsInRange": second_favorite_odds_in_range,
                "favoriteOddsOK": favorite_odds_ok,
                "isStakesOrTrial": is_stakes_or_trial
            }
        }
