import pytest
from unittest.mock import MagicMock, call, patch

from src.paddock_parser.models import Race, Runner
from src.paddock_parser.scorer import score_trifecta_factors
from src.paddock_parser.ui.terminal_ui import TerminalUI

# --- Test Data Fixture ---
@pytest.fixture
def sample_races_for_tiering():
    # Adding dummy data for required fields to satisfy the Race model's __init__
    dummy_time = "00:00"
    dummy_number = 1
    dummy_handicap = False
    return [
        # TIER 1: The "Perfect Match" (All 3 factors)
        # 2nd Fav > 4.0, Runners < 7, Fav > 1.0
        Race(race_id="T1_PERFECT", venue="Tier1", race_time=dummy_time, race_number=dummy_number, is_handicap=dummy_handicap, runners=[
            Runner(name="Fav", odds=1.5),
            Runner(name="2ndFav", odds=4.5),
            Runner(name="Other", odds=10.0)
        ]),
        # TIER 2: Two factors (2nd Fav > 4.0, Runners < 7, Fav <= 1.0)
        Race(race_id="T2_NO_FAV_ODDS", venue="Tier2", race_time=dummy_time, race_number=dummy_number, is_handicap=dummy_handicap, runners=[
            Runner(name="Fav", odds=0.8),
            Runner(name="2ndFav", odds=5.0)
        ]),
        # TIER 3: One factor (Runners < 7 only)
        Race(race_id="T3_ONLY_RUNNERS", venue="Tier3", race_time=dummy_time, race_number=dummy_number, is_handicap=dummy_handicap, runners=[
            Runner(name="Fav", odds=1.0),
            Runner(name="2ndFav", odds=2.0)
        ]),
        # TIER NULL: No factors (Runners > 7)
        Race(race_id="TNULL_TOO_MANY_RUNNERS", venue="TierNull", race_time=dummy_time, race_number=dummy_number, is_handicap=dummy_handicap, runners=[Runner(name=f"R{i}", odds=float(i+2)) for i in range(8)]),
    ]

# --- Test for "The Brain" (scorer.py) ---
def test_score_trifecta_factors_categorizes_correctly(sample_races_for_tiering):
    """
    SPEC: The scorer must correctly categorize races into three tiers based on the
    Project Lead's "Trifecta of Factors."
    """
    # Act
    tiered_results = score_trifecta_factors(sample_races_for_tiering)

    # Assert
    assert len(tiered_results["tier_1"]) == 1
    assert tiered_results["tier_1"][0].race_id == "T1_PERFECT"

    assert len(tiered_results["tier_2"]) == 1
    assert tiered_results["tier_2"][0].race_id == "T2_NO_FAV_ODDS"

    assert len(tiered_results["tier_3"]) == 1
    assert tiered_results["tier_3"][0].race_id == "T3_ONLY_RUNNERS"

# --- Tests for "The Face" (terminal_ui.py) ---
@patch('src.paddock_parser.ui.terminal_ui.Table')
@patch('src.paddock_parser.ui.terminal_ui.Console')
def test_display_tiered_dashboard_creates_multiple_tables(MockConsole, MockTable, sample_races_for_tiering):
    """
    SPEC: The UI must create three separate, correctly titled tables when presented
    with a full set of tiered data.
    """
    # Arrange
    mock_console_instance = MockConsole.return_value
    tiered_data = score_trifecta_factors(sample_races_for_tiering)
    ui = TerminalUI(console=mock_console_instance)

    # Act
    # The counts passed here don't matter for this test, as it asserts on the success path
    ui.display_tiered_dashboard(tiered_data, total_races=3, successful_adapter_count=1)

    # Assert
    # 1. It should have attempted to print three times (once for each table).
    assert mock_console_instance.print.call_count == 3

    # 2. It should have created three tables with the correct, distinct titles.
    assert MockTable.call_count == 3
    call_args_list = [call.kwargs['title'] for call in MockTable.call_args_list]
    assert "[bold green]== Tier 1: The Perfect Match ==[/bold green]" in call_args_list
    assert "[bold yellow]== Tier 2: The Strong Contenders ==[/bold yellow]" in call_args_list
    assert "[bold cyan]== Tier 3: The Singular Signals ==[/bold cyan]" in call_args_list

@patch('src.paddock_parser.ui.terminal_ui.Console')
def test_display_tiered_dashboard_shows_contextual_message_when_empty(MockConsole):
    """
    SPEC: The UI must show an informative message when no races meet the tier criteria.
    """
    # Arrange
    mock_console_instance = MockConsole.return_value
    empty_tiered_data = {"tier_1": [], "tier_2": [], "tier_3": []}
    ui = TerminalUI(console=mock_console_instance)

    # Act
    ui.display_tiered_dashboard(empty_tiered_data, total_races=50, successful_adapter_count=8)

    # Assert
    mock_console_instance.print.assert_called_once_with(
        "Found 50 races from 8 adapters, "
        "but [bold yellow]none met the criteria for the Tiered Dashboard.[/bold yellow]"
    )
