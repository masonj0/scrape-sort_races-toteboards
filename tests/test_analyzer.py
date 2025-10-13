import pytest
from decimal import Decimal
from datetime import datetime
from python_service.models import Race, Runner, OddsData
from python_service.analyzer import AnalyzerEngine, TrifectaAnalyzer, _get_best_win_odds

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
        # Race 1: Should PASS all criteria, will have a lower score
        Race(
            id="race_pass_1", venue="Test Park", race_number=1, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 3.0), # Favorite
                create_runner(2, 4.5), # Second Favorite
                create_runner(3, 5.0),
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
            runners=[create_runner(1, 2.0), create_runner(2, 4.5)]
        ),
        # Race 4: Should FAIL (Second favorite odds too low)
        Race(
            id="race_fail_2nd_fav_odds", venue="Test Park", race_number=4, start_time=datetime.now(), source="Test",
            runners=[create_runner(1, 3.0), create_runner(2, 3.5)]
        ),
        # Race 5: Should also PASS and have a higher score than race_pass_1
        Race(
            id="race_pass_2", venue="Test Park", race_number=5, start_time=datetime.now(), source="Test",
            runners=[
                create_runner(1, 4.0), # Favorite
                create_runner(2, 6.0), # Second Favorite
                create_runner(3, 8.0),
                create_runner(4, 12.0),
                create_runner(5, 15.0),
            ]
        ),
    ]

def test_analyzer_engine_discovery():
    """Tests that the AnalyzerEngine correctly discovers the TrifectaAnalyzer."""
    engine = AnalyzerEngine()
    assert 'trifecta' in engine.analyzers
    assert engine.analyzers['trifecta'] == TrifectaAnalyzer

def test_analyzer_engine_get_analyzer():
    """Tests that the AnalyzerEngine can instantiate a specific analyzer."""
    engine = AnalyzerEngine()
    analyzer = engine.get_analyzer('trifecta', max_field_size=8)
    assert isinstance(analyzer, TrifectaAnalyzer)
    assert analyzer.max_field_size == 8

def test_analyzer_engine_get_nonexistent_analyzer():
    """Tests that requesting a non-existent analyzer raises a ValueError."""
    engine = AnalyzerEngine()
    with pytest.raises(ValueError, match="Analyzer 'nonexistent' not found."):
        engine.get_analyzer('nonexistent')

def test_trifecta_analyzer_plugin_logic(sample_races_for_true_trifecta):
    """
    Tests the TrifectaAnalyzer's scoring, sorting, and new response structure.
    """
    engine = AnalyzerEngine()
    analyzer = engine.get_analyzer('trifecta')  # Use default criteria

    result = analyzer.qualify_races(sample_races_for_true_trifecta)

    # 1. Verify the new response structure
    assert isinstance(result, dict)
    assert "criteria" in result
    assert "races" in result
    assert result['criteria']['max_field_size'] == 10

    qualified_races = result['races']

    # 2. Check that the correct number of races were qualified
    assert len(qualified_races) == 2

    # 3. Check that the scores have been assigned and are valid numbers
    assert qualified_races[0].qualification_score is not None
    assert qualified_races[1].qualification_score is not None
    assert isinstance(qualified_races[0].qualification_score, float)

    # 4. Check that the races are sorted by score in descending order
    assert qualified_races[0].qualification_score > qualified_races[1].qualification_score
    assert qualified_races[0].id == "race_pass_2"  # This race should have the higher score
    assert qualified_races[1].id == "race_pass_1"

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

# Test case added by Operation: Resurrect and Modernize
from python_service.models import Race, Runner
import datetime

def test_trifecta_analyzer_rejects_races_with_too_few_runners(trifecta_analyzer):
    """Ensure analyzer rejects races with < 3 runners for a trifecta."""
    race_with_two_runners = Race(
        id='test_race_123',
        venue='TEST',
        race_number=1,
        start_time=datetime.datetime.now(),
        runners=[
            Runner(number=1, name='Horse A', odds='2/1', scratched=False),
            Runner(number=2, name='Horse B', odds='3/1', scratched=False)
        ],
        source='test'
    )

    is_qualified = trifecta_analyzer.is_race_qualified(race_with_two_runners)
    assert not is_qualified, 'Trifecta analyzer should not qualify a race with only two runners.'
