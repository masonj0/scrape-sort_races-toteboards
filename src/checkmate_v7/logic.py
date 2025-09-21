"""
Checkmate V7: `logic.py` - THE BRAIN
"""
from typing import List, Dict, Optional
from .models import RaceDataSchema, HorseSchema

class TrifectaAnalyzer:
    """
    Implements the "Dynamic Scorecard" for identifying Checkmate opportunities.
    This version uses a points-based system instead of a rigid binary filter.
    """

    def analyze_race(self, race: RaceDataSchema) -> Dict:
        """
        Analyzes a single race using a points-based scoring system.
        """
        if not race.horses or len(race.horses) < 2:
            return {
                "qualified": False,
                "checkmateScore": -100,
                "trifectaFactors": {
                    "fieldSize": {"ok": False, "points": -100, "reason": "Not enough horses to analyze."}
                }
            }

        # --- Factor Analysis ---

        # 1. Field Size Score
        num_runners = len(race.horses)
        if 4 <= num_runners <= 6:
            field_size_points = 30
            field_size_reason = f"Optimal field size ({num_runners} runners)"
        elif 7 <= num_runners <= 8:
            field_size_points = 10
            field_size_reason = f"Acceptable field size ({num_runners} runners)"
        else:
            field_size_points = -20
            field_size_reason = f"Too much chaos ({num_runners} runners)"

        # Sort horses by odds to find favorites
        sorted_horses = sorted(race.horses, key=lambda h: h.odds if h.odds is not None else float('inf'))
        favorite = sorted_horses[0]
        second_favorite = sorted_horses[1]

        # 2. Favorite's Odds Score
        if favorite.odds and favorite.odds > 1.5:
            fav_odds_points = 25
            fav_odds_reason = f"Favorite odds are not too low ({favorite.odds})"
        else:
            fav_odds_points = -50
            fav_odds_reason = f"Poor value favorite ({favorite.odds})"

        # 3. Second-Favorite's Odds Score
        if second_favorite.odds and 3.0 <= second_favorite.odds <= 9.0:
            sec_fav_odds_points = 45
            sec_fav_odds_reason = f"Second favorite in sweet spot ({second_favorite.odds})"
        else:
            sec_fav_odds_points = -15
            sec_fav_odds_reason = f"Second favorite outside range ({second_favorite.odds})"

        # --- Final Calculation ---

        total_score = field_size_points + fav_odds_points + sec_fav_odds_points
        is_qualified = total_score >= 70

        return {
            "checkmateScore": total_score,
            "qualified": is_qualified,
            "trifectaFactors": {
                "fieldSize": {
                    "ok": field_size_points > 0,
                    "points": field_size_points,
                    "reason": field_size_reason
                },
                "favoriteOdds": {
                    "ok": fav_odds_points > 0,
                    "points": fav_odds_points,
                    "reason": fav_odds_reason
                },
                "secondFavoriteOdds": {
                    "ok": sec_fav_odds_points > 0,
                    "points": sec_fav_odds_points,
                    "reason": sec_fav_odds_reason
                }
            }
        }
