from .models import RaceDataSchema
from .settings import settings

class TrifectaAnalyzer:
    """The corrected analyzer, fully aligned with the settings module."""

    def analyze_race(self, race: RaceDataSchema) -> dict:
        score = 0
        reasons = []
        trifecta_factors = {}

        if not race.horses:
            return {"qualified": False, "checkmateScore": 0, "reasons": ["No horses data."], "trifectaFactors": {}}

        horses_with_odds = sorted([h for h in race.horses if h.odds], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)

        # Field Size Logic - SOURCED FROM SETTINGS
        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX:
            points = settings.FIELD_SIZE_OPTIMAL_POINTS
            ok = True
            reason = f"Optimal field size ({num_runners} runners)"
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX:
            points = settings.FIELD_SIZE_ACCEPTABLE_POINTS
            ok = True
            reason = f"Acceptable field size ({num_runners} runners)"
        else:
            points = settings.FIELD_SIZE_PENALTY_POINTS
            ok = False
            reason = f"Field size not ideal ({num_runners} runners)"
        score += points
        reasons.append(reason)
        trifecta_factors["fieldSize"] = {"points": points, "ok": ok, "reason": reason}

        # Favorite and Contention Analysis - SOURCED FROM SETTINGS
        if num_runners >= 2:
            favorite, second_favorite = horses_with_odds[0], horses_with_odds[1]
            if favorite.odds <= settings.MAX_FAV_ODDS:
                points = settings.FAV_ODDS_POINTS
                ok = True
                reason = f"Favorite odds OK ({favorite.odds})"
            else:
                points = 0
                ok = False
                reason = f"Favorite odds too high ({favorite.odds})"
            score += points
            reasons.append(reason)
            trifecta_factors["favoriteOdds"] = {"points": points, "ok": ok, "reason": reason}

            if second_favorite.odds >= settings.MIN_2ND_FAV_ODDS:
                points = settings.SECOND_FAV_ODDS_POINTS
                ok = True
                reason = f"2nd Favorite odds OK ({second_favorite.odds})"
            else:
                points = 0
                ok = False
                reason = f"2nd Favorite odds too low ({second_favorite.odds})"
            score += points
            reasons.append(reason)
            trifecta_factors["secondFavoriteOdds"] = {"points": points, "ok": ok, "reason": reason}
        else:
            reasons.append("Not enough runners with odds for full analysis.")

        # QUALIFICATION_SCORE SOURCED FROM SETTINGS
        return {"qualified": score >= settings.QUALIFICATION_SCORE, "checkmateScore": score, "reasons": reasons, "trifectaFactors": trifecta_factors}