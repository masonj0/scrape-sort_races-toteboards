import pytest
from datetime import datetime, timedelta
from src.paddock_parser.models import Race, Runner # Models are now imported
from src.paddock_parser.scorer import get_high_roller_races, _convert_odds_to_float

# --- Test for the Odds Conversion Utility ---
@pytest.mark.parametrize("odds_str, expected_float", [
    ("10/1", 10.0), ("5/2", 2.5), ("1/2", 0.5), ("EVS", 1.0),
    ("SP", float('inf')), ("invalid", float('inf')),
])
def test_convert_odds_to_float(odds_str, expected_float):
    assert _convert_odds_to_float(odds_str) == expected_float

# --- Tests for the Main High Roller Logic ---
@pytest.fixture
def sample_races():
    now = datetime.now()
    return [
        Race(race_id="RACE_PERFECT", venue="Goodwood", race_time=(now + timedelta(minutes=10)).strftime("%H:%M"), is_handicap=False, runners=[Runner(name="Horse A", odds="4/1")]),
        Race(race_id="RACE_TOO_LATE", venue="Ascot", race_time=(now + timedelta(minutes=30)).strftime("%H:%M"), is_handicap=True, runners=[Runner(name="Horse C", odds="2/1")]),
        Race(race_id="RACE_TOO_MANY_RUNNERS", venue="York", race_time=(now + timedelta(minutes=15)).strftime("%H:%M"), is_handicap=False, runners=[Runner(name=f"Runner {i}", odds="10/1") for i in range(7)]), # Test edge case of 7 runners
        Race(race_id="RACE_HIGH_ODDS_FAV", venue="Newmarket", race_time=(now + timedelta(minutes=5)).strftime("%H:%M"), is_handicap=True, runners=[Runner(name="Horse E", odds="5/1")]),
        Race(race_id="RACE_LOW_ODDS_FAV", venue="Cheltenham", race_time=(now + timedelta(minutes=12)).strftime("%H:%M"), is_handicap=False, runners=[Runner(name="Horse G", odds="1/2")]),
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
