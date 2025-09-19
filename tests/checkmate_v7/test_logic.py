import pytest
from src.checkmate_v7.logic import TrifectaAnalyzer
from src.checkmate_v7.models import RaceDataSchema, HorseSchema

@pytest.fixture
def analyzer():
    return TrifectaAnalyzer()

@pytest.fixture
def qualifying_horses():
    """ A set of horses that meet the odds criteria. """
    # Corrected to use 'class_rating' as the key for instantiation
    return [
        HorseSchema(id="1", name="Favorite", number=1, jockey="A", trainer="B", odds=2.0, morningLine=2.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="2", name="Second Fav", number=2, jockey="C", trainer="D", odds=4.0, morningLine=4.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="3", name="Longshot", number=3, jockey="E", trainer="F", odds=10.0, morningLine=10.0, speed=80, class_rating=80, form="", lastRaced=""),
    ]

def test_qualifying_race(analyzer, qualifying_horses):
    """ Tests a race that should qualify based on all three core factors. """
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=qualifying_horses, conditions="Clear", distance="6f", surface="Dirt")

    result = analyzer.analyze_race(race)

    assert result["qualified"] is True
    assert result["score"] == 3
    assert result["trifectaFactors"]["fieldSizeOK"] is True
    assert result["trifectaFactors"]["secondFavoriteOddsInRange"] is True
    assert result["trifectaFactors"]["favoriteOddsOK"] is True
    assert result["trifectaFactors"]["isStakesOrTrial"] is False

def test_non_qualifying_race_by_field_size(analyzer, qualifying_horses):
    """ Tests a race that fails due to having too many runners. """
    # Add more horses to exceed the field size limit
    horses = qualifying_horses + [
        HorseSchema(id="4", name="H4", number=4, jockey="G", trainer="H", odds=12.0, morningLine=12.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="5", name="H5", number=5, jockey="I", trainer="J", odds=15.0, morningLine=15.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="6", name="H6", number=6, jockey="K", trainer="L", odds=20.0, morningLine=20.0, speed=80, class_rating=80, form="", lastRaced=""),
        HorseSchema(id="7", name="H7", number=7, jockey="M", trainer="N", odds=25.0, morningLine=25.0, speed=80, class_rating=80, form="", lastRaced=""),
    ]
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=horses, conditions="Clear", distance="6f", surface="Dirt")

    result = analyzer.analyze_race(race)

    assert result["qualified"] is False
    assert result["trifectaFactors"]["fieldSizeOK"] is False

def test_non_qualifying_race_by_odds(analyzer, qualifying_horses):
    """ Tests a race that fails due to the favorite's odds being too low. """
    qualifying_horses[0].odds = 1.4 # Set favorite's odds to be too low (< 1.5)
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=qualifying_horses, conditions="Clear", distance="6f", surface="Dirt")

    result = analyzer.analyze_race(race)

    assert result["qualified"] is False
    assert result["trifectaFactors"]["favoriteOddsOK"] is False

def test_stakes_race_bonus_score(analyzer, qualifying_horses):
    """ Tests that a qualifying race gets a score bonus for being a stakes race. """
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=qualifying_horses, conditions="Graded Stakes", distance="1m", surface="Turf")

    result = analyzer.analyze_race(race)

    assert result["qualified"] is True
    assert result["score"] == 4 # 3 for core factors + 1 for stakes
    assert result["trifectaFactors"]["isStakesOrTrial"] is True

def test_empty_race_is_handled(analyzer):
    """ Tests that a race with no horses is handled gracefully. """
    race = RaceDataSchema(id="R1", track="Test", raceNumber=1, postTime="1PM", horses=[], conditions="Clear", distance="6f", surface="Dirt")

    result = analyzer.analyze_race(race)

    assert result["qualified"] is False
    assert result["score"] == 0
