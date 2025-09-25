# src/checkmate_v7/logic.py
from .models import RaceDataSchema
from .settings import settings

class TrifectaAnalyzer:
    def analyze_race(self, race: RaceDataSchema) -> dict:
        """
        Analyzes a single race to determine its suitability for a trifecta bet
        based on a proprietary scoring model defined by the test specifications.
        """
        num_runners = len(race.horses)

        # Factor 1: Field Size Score
        if 4 <= num_runners <= 6:
            field_size_points = 30
            field_size_reason = f"Optimal field size ({num_runners} runners)"
        elif 7 <= num_runners <= 8:
            field_size_points = 10
            field_size_reason = f"Acceptable field size ({num_runners} runners)"
        elif num_runners >= 9:
            field_size_points = -20
            field_size_reason = f"Too much chaos ({num_runners} runners)"
        else: # 0-3 runners
            return {
                "checkmateScore": 0,
                "qualified": False,
                "trifectaFactors": {
                    "fieldSize": {"points": 0, "reason": "Field too small for analysis."}
                }
            }

        # Sort horses by odds to find favorites
        sorted_horses = sorted([h for h in race.horses if h.odds is not None and h.odds > 0], key=lambda h: h.odds)

        if len(sorted_horses) < 2:
            return {
                "checkmateScore": 0,
                "qualified": False,
                "trifectaFactors": {
                    "fieldSize": {"points": field_size_points, "reason": field_size_reason},
                    "favoriteOdds": {"points": 0, "reason": "Not enough horses with odds to determine favorites."},
                    "secondFavoriteOdds": {"points": 0, "reason": "Not enough horses with odds to determine favorites."}
                }
            }

        favorite = sorted_horses[0]
        second_favorite = sorted_horses[1]

        # Factor 2: Favorite Odds Score
        if favorite.odds > settings.MIN_FAV_ODDS:
            fav_odds_points = 25
            fav_odds_reason = f"Favorite odds are not too low ({favorite.odds})"
        else:
            fav_odds_points = -50
            fav_odds_reason = f"Poor value favorite ({favorite.odds})"

        # Factor 3: Second Favorite Odds Score
        if settings.MIN_2ND_FAV_ODDS <= second_favorite.odds <= settings.MAX_2ND_FAV_ODDS:
            sec_fav_odds_points = 45
            sec_fav_odds_reason = f"Second favorite in sweet spot ({second_favorite.odds})"
        else:
            sec_fav_odds_points = -15
            sec_fav_odds_reason = f"Second favorite outside range ({second_favorite.odds})"

        # Calculate final score and qualification
        total_score = field_size_points + fav_odds_points + sec_fav_odds_points
        is_qualified = total_score >= settings.QUALIFICATION_SCORE

        return {
            "checkmateScore": total_score,
            "qualified": is_qualified,
            "trifectaFactors": {
                "fieldSize": {
                    "points": field_size_points,
                    "reason": field_size_reason
                },
                "favoriteOdds": {
                    "points": fav_odds_points,
                    "reason": fav_odds_reason
                },
                "secondFavoriteOdds": {
                    "points": sec_fav_odds_points,
                    "reason": sec_fav_odds_reason
                }
            }
        }