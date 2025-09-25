# src/checkmate_v7/logic.py
from .models import RaceDataSchema
from .settings import settings

class TrifectaAnalyzer:
    def analyze_race(self, race: RaceDataSchema) -> dict:
        score = 0
        reasons = []
        trifecta_factors = {}

        if not race.horses:
            return {"qualified": False, "checkmateScore": 0, "reasons": ["No horses data."], "trifectaFactors": trifecta_factors}

        horses_with_odds = sorted([h for h in race.horses if h.odds], key=lambda h: h.odds)

        # Field Size Check
        field_size = len(horses_with_odds)
        if 4 <= field_size <= 6:
            field_size_points = 30
            field_size_ok = True
            field_size_reason = f"Optimal field size ({field_size} runners)"
        elif 7 <= field_size <= 8:
            field_size_points = 10
            field_size_ok = True
            field_size_reason = f"Acceptable field size ({field_size} runners)"
        else:
            field_size_points = -20
            field_size_ok = False
            field_size_reason = f"Too much chaos ({field_size} runners)" if field_size > 8 else f"Field too small ({field_size} runners)"
        score += field_size_points
        reasons.append(field_size_reason)
        trifecta_factors["fieldSize"] = {"points": field_size_points, "ok": field_size_ok, "reason": field_size_reason}


        # Favorite and Contention Analysis
        if len(horses_with_odds) >= 2:
            favorite, second_favorite = horses_with_odds[0], horses_with_odds[1]

            fav_odds = favorite.odds
            if fav_odds > 1.5:
                fav_points = 25
                fav_ok = True
                fav_reason = f"Favorite odds are not too low ({fav_odds})"
            else:
                fav_points = -50
                fav_ok = False
                fav_reason = f"Poor value favorite ({fav_odds})"
            score += fav_points
            reasons.append(fav_reason)
            trifecta_factors["favoriteOdds"] = {"points": fav_points, "ok": fav_ok, "reason": fav_reason}

            sec_fav_odds = second_favorite.odds
            if 3.0 <= sec_fav_odds <= 9.0:
                sec_fav_points = 45
                sec_fav_ok = True
                sec_fav_reason = f"Second favorite in sweet spot ({sec_fav_odds})"
            else:
                sec_fav_points = -15
                sec_fav_ok = False
                sec_fav_reason = f"Second favorite outside range ({sec_fav_odds})"
            score += sec_fav_points
            reasons.append(sec_fav_reason)
            trifecta_factors["secondFavoriteOdds"] = {"points": sec_fav_points, "ok": sec_fav_ok, "reason": sec_fav_reason}
        else:
            reasons.append("Not enough runners with odds for full analysis.")

        return {"qualified": score >= 70, "checkmateScore": score, "reasons": reasons, "trifectaFactors": trifecta_factors}