import pytest
from src.checkmate_v7.logic import TrifectaAnalyzer
from src.checkmate_v7.models import RaceDataSchema, HorseSchema
from src.checkmate_v7.settings import settings

@pytest.fixture
def analyzer():
    """Provides a TrifectaAnalyzer instance."""
    return TrifectaAnalyzer()

@pytest.fixture
def base_horses():
    """Provides a base list of horses with neutral odds for testing."""
    return [
        HorseSchema(id="1", name="Horse A", number=1, jockey="J1", trainer="T1", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="2", name="Horse B", number=2, jockey="J2", trainer="T2", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="3", name="Horse C", number=3, jockey="J3", trainer="T3", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="4", name="Horse D", number=4, jockey="J4", trainer="T4", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="5", name="Horse E", number=5, jockey="J5", trainer="T5", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="6", name="Horse F", number=6, jockey="J6", trainer="T6", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="7", name="Horse G", number=7, jockey="J7", trainer="T7", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="8", name="Horse H", number=8, jockey="J8", trainer="T8", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="9", name="Horse I", number=9, jockey="J9", trainer="T9", odds=5.0, morningLine=5.0, speed=80, class_rating=80, form="", lastRaced=""),
    ]

def test_perfect_score_is_qualified(analyzer, base_horses):
    """
    SPEC: A race with optimal conditions should receive a perfect score and be qualified.
    - Field Size: 5 runners (+30)
    - Favorite Odds: <= 3.5 (+30)
    - Second Favorite Odds: >= 4.0 (+40)
    Total: 30 + 30 + 40 = 100
    """
    horses = base_horses[:5]
    horses[0].odds = 2.0 # Favorite
    horses[1].odds = 4.0 # Second Favorite
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=horses, conditions="Stakes", distance="1m", surface="Turf")

    result = analyzer.analyze_race(race)

    assert result["checkmateScore"] == settings.FIELD_SIZE_OPTIMAL_POINTS + settings.FAV_ODDS_POINTS + settings.SECOND_FAV_ODDS_POINTS
    assert result["qualified"] is True
    assert result["trifectaFactors"]["fieldSize"]["points"] == settings.FIELD_SIZE_OPTIMAL_POINTS
    assert result["trifectaFactors"]["favoriteOdds"]["points"] == settings.FAV_ODDS_POINTS
    assert result["trifectaFactors"]["secondFavoriteOdds"]["points"] == settings.SECOND_FAV_ODDS_POINTS

def test_field_size_scoring(analyzer, base_horses):
    """
    SPEC: Field size should award points correctly based on settings.
    """
    # Test optimal case (5 runners)
    race_optimal = RaceDataSchema(id="R_opt", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:5], conditions="C", distance="D", surface="S")
    res_optimal = analyzer.analyze_race(race_optimal)
    assert res_optimal["trifectaFactors"]["fieldSize"]["points"] == settings.FIELD_SIZE_OPTIMAL_POINTS
    assert "Optimal field size (5 runners)" in res_optimal["reasons"][0]

    # Test acceptable case (7 runners)
    race_acceptable = RaceDataSchema(id="R_acc", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:7], conditions="C", distance="D", surface="S")
    res_acceptable = analyzer.analyze_race(race_acceptable)
    assert res_acceptable["trifectaFactors"]["fieldSize"]["points"] == settings.FIELD_SIZE_ACCEPTABLE_POINTS
    assert "Acceptable field size (7 runners)" in res_acceptable["reasons"][0]

    # Test penalty case (9 runners)
    race_penalty = RaceDataSchema(id="R_pen", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:9], conditions="C", distance="D", surface="S")
    res_penalty = analyzer.analyze_race(race_penalty)
    assert res_penalty["trifectaFactors"]["fieldSize"]["points"] == settings.FIELD_SIZE_PENALTY_POINTS
    assert "Field size not ideal (9 runners)" in res_penalty["reasons"][0]

def test_favorite_odds_scoring(analyzer, base_horses):
    """
    SPEC: Favorite's odds score should be correct based on settings.
    """
    horses = base_horses[:5]
    # Test good odds (<= MAX_FAV_ODDS)
    horses[0].odds = settings.MAX_FAV_ODDS - 0.1
    race_good = RaceDataSchema(id="R_good", track="T", raceNumber=1, postTime="1PM", horses=horses, conditions="C", distance="D", surface="S")
    res_good = analyzer.analyze_race(race_good)
    assert res_good["trifectaFactors"]["favoriteOdds"]["points"] == settings.FAV_ODDS_POINTS
    assert f"Favorite odds OK ({settings.MAX_FAV_ODDS - 0.1})" in res_good["reasons"][1]

    # Test poor odds (> MAX_FAV_ODDS)
    horses[0].odds = settings.MAX_FAV_ODDS + 0.1
    race_poor = RaceDataSchema(id="R_poor", track="T", raceNumber=1, postTime="1PM", horses=horses, conditions="C", distance="D", surface="S")
    res_poor = analyzer.analyze_race(race_poor)
    assert res_poor["trifectaFactors"]["favoriteOdds"]["points"] == 0
    assert f"Favorite odds too high ({settings.MAX_FAV_ODDS + 0.1})" in res_poor["reasons"][1]

def test_second_favorite_odds_scoring(analyzer, base_horses):
    """
    SPEC: Second favorite's odds should be correct based on settings.
    """
    horses = base_horses[:5]
    horses[0].odds = 2.0 # Set favorite to ensure sorting

    # Test good odds (>= MIN_2ND_FAV_ODDS)
    horses[1].odds = settings.MIN_2ND_FAV_ODDS + 1.0
    race_good = RaceDataSchema(id="R_good", track="T", raceNumber=1, postTime="1PM", horses=horses, conditions="C", distance="D", surface="S")
    res_good = analyzer.analyze_race(race_good)
    assert res_good["trifectaFactors"]["secondFavoriteOdds"]["points"] == settings.SECOND_FAV_ODDS_POINTS
    assert f"2nd Favorite odds OK ({settings.MIN_2ND_FAV_ODDS + 1.0})" in res_good["reasons"][2]

    # Test poor odds (< MIN_2ND_FAV_ODDS)
    horses[1].odds = settings.MIN_2ND_FAV_ODDS - 1.0
    race_poor = RaceDataSchema(id="R_poor", track="T", raceNumber=1, postTime="1PM", horses=horses, conditions="C", distance="D", surface="S")
    res_poor = analyzer.analyze_race(race_poor)
    assert res_poor["trifectaFactors"]["secondFavoriteOdds"]["points"] == 0
    assert f"2nd Favorite odds too low ({settings.MIN_2ND_FAV_ODDS - 1.0})" in res_poor["reasons"][2]

def test_qualification_threshold(analyzer, base_horses):
    """
    SPEC: A race is qualified if checkmateScore is >= QUALIFICATION_SCORE.
    """
    # Score = 30 (size) + 30 (fav) + 40 (2nd fav) = 100. Should qualify.
    horses_qual = base_horses[:5]
    horses_qual[0].odds = 2.0
    horses_qual[1].odds = 4.0
    race_qual = RaceDataSchema(id="R_qual", track="T", raceNumber=1, postTime="1PM", horses=horses_qual, conditions="C", distance="D", surface="S")
    res_qual = analyzer.analyze_race(race_qual)
    assert res_qual["checkmateScore"] >= settings.QUALIFICATION_SCORE
    assert res_qual["qualified"] is True

    # Score = -20 (size) + 0 (fav) + 0 (2nd fav) = -20. Should not qualify.
    horses_no_qual = base_horses[:9] # 9 runners = -20 points
    horses_no_qual[0].odds = 4.0 # > 3.5 = 0 points
    horses_no_qual[1].odds = 3.0 # < 4.0 = 0 points
    race_no_qual = RaceDataSchema(id="R_no_qual", track="T", raceNumber=1, postTime="1PM", horses=horses_no_qual, conditions="C", distance="D", surface="S")
    res_no_qual = analyzer.analyze_race(race_no_qual)
    assert res_no_qual["checkmateScore"] < settings.QUALIFICATION_SCORE
    assert res_no_qual["qualified"] is False