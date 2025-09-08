import pytest
from unittest.mock import patch, call, AsyncMock
from datetime import datetime
from paddock_parser.models import Race as ScorerRace, Runner as ScorerRunner
from paddock_parser.base import NormalizedRace, NormalizedRunner
from paddock_parser.ui.terminal_ui import TerminalUI

@pytest.fixture
def sample_scored_races():
    """Fixture for a list of scored races, now returning NormalizedRace as the pipeline does."""
    race1 = NormalizedRace(
        race_id="R1", track_name="Newmarket", race_number=1, post_time=datetime(2025, 9, 7, 14, 30),
        number_of_runners=8, race_type="Handicap"
    )
    setattr(race1, 'score', 2.5)
    setattr(race1, 'scores', {
        "total_score": 2.5, "field_size_score": 0.125,
        "favorite_odds_score": 2.0, "contention_score": 5.0
    })

    race2 = NormalizedRace(
        race_id="R2", track_name="Goodwood", race_number=2, post_time=datetime(2025, 9, 7, 14, 45),
        number_of_runners=10, race_type="Stakes"
    )
    setattr(race2, 'score', 1.8)
    setattr(race2, 'scores', {
        "total_score": 1.8, "field_size_score": 0.1,
        "favorite_odds_score": 4.5, "contention_score": 1.0
    })
    # The pipeline already sorts them, so the test should expect sorted input
    return [race1, race2]

@patch('paddock_parser.ui.terminal_ui.Table')
@patch('paddock_parser.ui.terminal_ui.Console')
def test_display_scoring_report_uses_rich_table(MockConsole, MockTable, sample_scored_races):
    mock_console_instance = MockConsole()
    mock_table_instance = MockTable.return_value
    ui = TerminalUI(console=mock_console_instance)

    ui.display_scoring_report(sample_scored_races)

    MockTable.assert_called_once_with(title="[bold green]Dynamic Scoring Report[/bold green]")

    expected_calls = [
        call("Race Time", style="cyan"),
        call("Venue", style="magenta"),
        call("Race #", style="white"),
        call("Runners", style="white"),
        call("Handicap", style="white"),
        call("Fav Odds", style="yellow"),
        call("Contention", style="yellow"),
        call("Field Size", style="yellow"),
        call("Total Score", style="bold green"),
    ]
    mock_table_instance.add_column.assert_has_calls(expected_calls, any_order=False)
    assert mock_table_instance.add_column.call_count == len(expected_calls)

    expected_row_calls = [
        call('14:30', 'Newmarket', '1', '8', 'Yes', '2.00', '5.00', '0.125', '2.50'),
        call('14:45', 'Goodwood', '2', '10', 'No', '4.50', '1.00', '0.100', '1.80'),
    ]
    mock_table_instance.add_row.assert_has_calls(expected_row_calls)
    assert mock_table_instance.add_row.call_count == len(sample_scored_races)

    mock_console_instance.print.assert_called_once_with(mock_table_instance)

@pytest.mark.anyio
@patch('paddock_parser.ui.terminal_ui.run_pipeline', new_callable=AsyncMock)
@patch('paddock_parser.ui.terminal_ui.TerminalUI.display_scoring_report')
@patch('paddock_parser.ui.terminal_ui.Console')
async def test_run_scoring_report_orchestrates_correctly(
    MockConsole, MockDisplay, MockRunPipeline, sample_scored_races
):
    # Setup mocks
    mock_console_instance = MockConsole()
    MockRunPipeline.return_value = sample_scored_races
    ui = TerminalUI(console=mock_console_instance)

    # Run the async method
    await ui._run_scoring_report()

    # Assertions
    mock_console_instance.status.assert_called_once_with("Fetching data from providers...", spinner="dots")
    MockRunPipeline.assert_called_once()
    MockDisplay.assert_called_once_with(sample_scored_races)
