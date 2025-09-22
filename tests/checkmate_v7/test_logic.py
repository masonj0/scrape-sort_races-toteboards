import pytest
from src.checkmate_v7.logic import TrifectaAnalyzer
from src.checkmate_v7.models import RaceDataSchema, HorseSchema

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
    ]

def test_perfect_score_is_qualified(analyzer, base_horses):
    """
    SPEC: A race with optimal conditions should receive a perfect score (100) and be qualified.
    - Field Size: 5 runners (+30)
    - Favorite Odds: > 1.5 (+25)
    - Second Favorite Odds: 3.0-9.0 (+45)
    """
    base_horses[0].odds = 2.0 # Favorite
    base_horses[1].odds = 4.0 # Second Favorite
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=base_horses, conditions="Stakes", distance="1m", surface="Turf")

    result = analyzer.analyze_race(race)

    assert result["checkmateScore"] == 100
    assert result["qualified"] is True
    assert result["trifectaFactors"]["fieldSize"]["points"] == 30
    assert result["trifectaFactors"]["favoriteOdds"]["points"] == 25
    assert result["trifectaFactors"]["secondFavoriteOdds"]["points"] == 45

def test_field_size_scoring(analyzer, base_horses):
    """
    SPEC: Field size should award points correctly.
    - 4-6 runners: +30
    - 7-8 runners: +10
    - 9+ runners: -20
    """
    # Test optimal case (5 runners)
    race_optimal = RaceDataSchema(id="R_opt", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:5], conditions="C", distance="D", surface="S")
    res_optimal = analyzer.analyze_race(race_optimal)
    assert res_optimal["trifectaFactors"]["fieldSize"]["points"] == 30
    assert "Optimal field size (5 runners)" in res_optimal["trifectaFactors"]["fieldSize"]["reason"]

    # Test acceptable case (7 runners)
    race_acceptable = RaceDataSchema(id="R_acc", track="T", raceNumber=1, postTime="1PM", horses=base_horses * 2, conditions="C", distance="D", surface="S")
    race_acceptable.horses = race_acceptable.horses[:7]
    res_acceptable = analyzer.analyze_race(race_acceptable)
    assert res_acceptable["trifectaFactors"]["fieldSize"]["points"] == 10
    assert "Acceptable field size (7 runners)" in res_acceptable["trifectaFactors"]["fieldSize"]["reason"]

    # Test chaos case (9 runners)
    race_chaos = RaceDataSchema(id="R_chaos", track="T", raceNumber=1, postTime="1PM", horses=base_horses * 2, conditions="C", distance="D", surface="S")
    res_chaos = analyzer.analyze_race(race_chaos)
    assert res_chaos["trifectaFactors"]["fieldSize"]["points"] == -20
    assert "Too much chaos (10 runners)" in res_chaos["trifectaFactors"]["fieldSize"]["reason"]

def test_favorite_odds_scoring(analyzer, base_horses):
    """
    SPEC: Favorite's odds score should be +25 for > 1.5, -50 for <= 1.5
    """
    # Test good odds
    base_horses[0].odds = 2.5
    race_good = RaceDataSchema(id="R_good", track="T", raceNumber=1, postTime="1PM", horses=base_horses, conditions="C", distance="D", surface="S")
    res_good = analyzer.analyze_race(race_good)
    assert res_good["trifectaFactors"]["favoriteOdds"]["points"] == 25
    assert "Favorite odds are not too low (2.5)" in res_good["trifectaFactors"]["favoriteOdds"]["reason"]

    # Test poor odds
    base_horses[0].odds = 1.4
    race_poor = RaceDataSchema(id="R_poor", track="T", raceNumber=1, postTime="1PM", horses=base_horses, conditions="C", distance="D", surface="S")
    res_poor = analyzer.analyze_race(race_poor)
    assert res_poor["trifectaFactors"]["favoriteOdds"]["points"] == -50
    assert "Poor value favorite (1.4)" in res_poor["trifectaFactors"]["favoriteOdds"]["reason"]

def test_second_favorite_odds_scoring(analyzer, base_horses):
    """
    SPEC: Second favorite's odds should be +45 for 3.0-9.0, -15 otherwise.
    """
    base_horses[0].odds = 2.0 # Set favorite to ensure sorting

    # Test sweet spot
    base_horses[1].odds = 5.0
    race_good = RaceDataSchema(id="R_good", track="T", raceNumber=1, postTime="1PM", horses=base_horses, conditions="C", distance="D", surface="S")
    res_good = analyzer.analyze_race(race_good)
    assert res_good["trifectaFactors"]["secondFavoriteOdds"]["points"] == 45
    assert "Second favorite in sweet spot (5.0)" in res_good["trifectaFactors"]["secondFavoriteOdds"]["reason"]

    # Test outside range (too low)
    base_horses[1].odds = 2.5
    race_low = RaceDataSchema(id="R_low", track="T", raceNumber=1, postTime="1PM", horses=base_horses, conditions="C", distance="D", surface="S")
    res_low = analyzer.analyze_race(race_low)
    assert res_low["trifectaFactors"]["secondFavoriteOdds"]["points"] == -15
    assert "Second favorite outside range (2.5)" in res_low["trifectaFactors"]["secondFavoriteOdds"]["reason"]

    # Test outside range (too high)
    # Reset other odds to be high to ensure sorting is correct
    base_horses[2].odds = 12.0
    base_horses[3].odds = 13.0
    base_horses[4].odds = 14.0
    base_horses[1].odds = 10.0
    race_high = RaceDataSchema(id="R_high", track="T", raceNumber=1, postTime="1PM", horses=base_horses, conditions="C", distance="D", surface="S")
    res_high = analyzer.analyze_race(race_high)
    assert res_high["trifectaFactors"]["secondFavoriteOdds"]["points"] == -15
    assert "Second favorite outside range (10.0)" in res_high["trifectaFactors"]["secondFavoriteOdds"]["reason"]

def test_qualification_threshold(analyzer, base_horses):
    """
    SPEC: A race is qualified if checkmateScore is 70 or greater.
    """
    # Score = 30 (size) + 25 (fav) + 45 (2nd fav) = 100. Should qualify.
    base_horses[0].odds = 2.0
    base_horses[1].odds = 4.0
    race_qual = RaceDataSchema(id="R_qual", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:5], conditions="C", distance="D", surface="S")
    res_qual = analyzer.analyze_race(race_qual)
    assert res_qual["checkmateScore"] >= 70
    assert res_qual["qualified"] is True

    # Score = 30 (size) + (-50) (fav) + 45 (2nd fav) = 25. Should not qualify.
    base_horses[0].odds = 1.2
    base_horses[1].odds = 4.0
    race_no_qual = RaceDataSchema(id="R_no_qual", track="T", raceNumber=1, postTime="1PM", horses=base_horses[:5], conditions="C", distance="D", surface="S")
    res_no_qual = analyzer.analyze_race(race_no_qual)
    assert res_no_qual["checkmateScore"] < 70
    assert res_no_qual["qualified"] is False
