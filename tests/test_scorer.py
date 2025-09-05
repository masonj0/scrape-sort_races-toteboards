import pytest
from datetime import datetime, timedelta
from src.paddock_parser.models import Race, Runner
from src.paddock_parser.scorer import get_high_roller_races, calculate_weighted_score

# --- Tests for the Main High Roller Logic ---
@pytest.fixture
def sample_races():
    now = datetime.now()
    return [
        Race(race_id="RACE_PERFECT", venue="Goodwood", race_time=(now + timedelta(minutes=10)).strftime("%H:%M"), race_number=1, is_handicap=False, runners=[Runner(name="Horse A", odds=4.0)]),
        Race(race_id="RACE_TOO_LATE", venue="Ascot", race_time=(now + timedelta(minutes=30)).strftime("%H:%M"), race_number=2, is_handicap=True, runners=[Runner(name="Horse C", odds=2.0)]),
        Race(race_id="RACE_TOO_MANY_RUNNERS", venue="York", race_time=(now + timedelta(minutes=15)).strftime("%H:%M"), race_number=3, is_handicap=False, runners=[Runner(name=f"Runner {i}", odds=10.0) for i in range(7)]), # Test edge case of 7 runners
        Race(race_id="RACE_HIGH_ODDS_FAV", venue="Newmarket", race_time=(now + timedelta(minutes=5)).strftime("%H:%M"), race_number=4, is_handicap=True, runners=[Runner(name="Horse E", odds=5.0)]),
        Race(race_id="RACE_LOW_ODDS_FAV", venue="Cheltenham", race_time=(now + timedelta(minutes=12)).strftime("%H:%M"), race_number=5, is_handicap=False, runners=[Runner(name="Horse G", odds=0.5)]),
    ]

def test_filters_races_correctly(sample_races):
    now = datetime.now()
    high_roller_races = get_high_roller_races(sample_races, now)
    race_ids = {race.race_id for race in high_roller_races}
    assert len(high_roller_races) == 3
    assert "RACE_PERFECT" in race_ids
    assert "RACE_HIGH_ODDS_FAV" in race_ids
    assert "RACE_LOW_ODDS_FAV" in race_ids

def test_sorts_races_by_high_roller_score(sample_races):
    now = datetime.now()
    sorted_races = get_high_roller_races(sample_races, now)
    assert len(sorted_races) == 3
    assert sorted_races[0].race_id == "RACE_HIGH_ODDS_FAV"
    assert sorted_races[1].race_id == "RACE_PERFECT"
    assert sorted_races[2].race_id == "RACE_LOW_ODDS_FAV"


def test_calculate_weighted_score():
    """
    SPEC: The weighted score must correctly apply weights to different race factors.
    - A lower runner count should increase the score.
    - Higher odds for the favorite should increase the score.
    """
    # Arrange: A sample race with a clear favorite
    race = Race(
        race_id="R1", venue="Test", race_time="14:00", source="Test", race_number=1, is_handicap=False,
        runners=[
            Runner(name="Favorite", odds=2.5),
            Runner(name="Longshot", odds=10.0)
        ]
    )
    # Arrange: Sample weights from our V3 strategy
    weights = {
        "FIELD_SIZE_WEIGHT": 0.6,
        "FAVORITE_ODDS_WEIGHT": 0.4
    }
    # Act

    # Act
    actual_score = calculate_weighted_score(race, weights)

    # Assert
    assert actual_score == pytest.approx(1.3)
