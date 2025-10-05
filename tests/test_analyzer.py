import pytest
from decimal import Decimal
from datetime import datetime
from python_service.models import Race, Runner, OddsData
from python_service.analyzer import TrifectaAnalyzer, _get_best_win_odds

# Helper to create runners for tests
def create_runner(number, odds_val=None, scratched=False):
    odds_data = {}
    if odds_val:
        odds_data["TestOdds"] = OddsData(win=Decimal(str(odds_val)), source="TestOdds", last_updated=datetime.now())
    return Runner(number=number, name=f"Runner {number}", odds=odds_data, scratched=scratched)

@pytest.fixture
def sample_races_for_true_trifecta():
    """Provides a list of sample Race objects for the new 'True Trifecta' logic."""
    return [
        # Race 1: Should PASS all criteria
        Race(
            id="race_pass_1", venue="Test Park", race_number=1, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 3.0), # Favorite
                create_runner(2, 4.5), # Second Favorite
                create_runner(3, 5.0),
                create_runner(4, 8.0),
                create_runner(5, 10.0),
            ]
        ),
        # Race 2: Should FAIL (Field size too large)
        Race(
            id="race_fail_field_size", venue="Test Park", race_number=2, start_time=datetime.now(), source="Test",
            runners=[create_runner(i, 5.0 + i) for i in range(1, 12)] # 11 runners
        ),
        # Race 3: Should FAIL (Favorite odds too low)
        Race(
            id="race_fail_fav_odds", venue="Test Park", race_number=3, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 2.0), # Favorite odds < 2.5
                create_runner(2, 4.5),
                create_runner(3, 5.0),
            ]
        ),
        # Race 4: Should FAIL (Second favorite odds too low)
        Race(
            id="race_fail_2nd_fav_odds", venue="Test Park", race_number=4, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 3.0),
                create_runner(2, 3.5), # Second favorite odds < 4.0
                create_runner(3, 5.0),
            ]
        ),
        # Race 5: Should FAIL (Not enough runners with odds)
        Race(
            id="race_fail_not_enough_odds", venue="Test Park", race_number=5, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 3.0),
                create_runner(2), # No odds
                create_runner(3), # No odds
            ]
        ),
        # Race 6: Should PASS (scratched runner ignored, still meets criteria)
        Race(
            id="race_pass_scratched", venue="Test Park", race_number=6, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 3.0),
                create_runner(2, 4.5),
                create_runner(3, 5.0),
                create_runner(4, 8.0, scratched=True),
            ]
        ),
    ]

def test_true_trifecta_analyzer_qualifies_correct_races(sample_races_for_true_trifecta):
    """
    Tests that the analyzer correctly identifies races that meet the new
    'True Trifecta' qualification criteria.
    """
    analyzer = TrifectaAnalyzer() # Use default criteria
    qualified_races = analyzer.qualify_races(sample_races_for_true_trifecta)

    qualified_ids = {race.id for race in qualified_races}

    assert "race_pass_1" in qualified_ids
    assert "race_pass_scratched" in qualified_ids
    assert len(qualified_races) == 2

def test_true_trifecta_analyzer_filters_incorrect_races(sample_races_for_true_trifecta):
    """
    Tests that the analyzer correctly filters out races that do not meet
    the new 'True Trifecta' qualification criteria.
    """
    analyzer = TrifectaAnalyzer() # Use default criteria
    qualified_races = analyzer.qualify_races(sample_races_for_true_trifecta)

    qualified_ids = {race.id for race in qualified_races}

    assert "race_fail_field_size" not in qualified_ids
    assert "race_fail_fav_odds" not in qualified_ids
    assert "race_fail_2nd_fav_odds" not in qualified_ids
    assert "race_fail_not_enough_odds" not in qualified_ids

def test_get_best_win_odds_helper():
    """Tests the helper function for finding the best odds."""
    runner_with_odds = create_runner(1)
    runner_with_odds.odds = {
        "SourceA": OddsData(win=Decimal("3.0"), source="A", last_updated=datetime.now()),
        "SourceB": OddsData(win=Decimal("2.5"), source="B", last_updated=datetime.now()),
    }
    assert _get_best_win_odds(runner_with_odds) == Decimal("2.5")

    runner_no_odds = create_runner(2)
    assert _get_best_win_odds(runner_no_odds) is None

    runner_no_win = create_runner(3)
    runner_no_win.odds = {"SourceA": OddsData(win=None, source="A", last_updated=datetime.now())}
    assert _get_best_win_odds(runner_no_win) is None