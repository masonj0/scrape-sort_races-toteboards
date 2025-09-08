import pytest
from unittest.mock import patch, call
from datetime import datetime
from paddock_parser.models import Race, Runner
from paddock_parser.base import NormalizedRace, NormalizedRunner
from paddock_parser.ui.terminal_ui import TerminalUI

@pytest.fixture
def sample_high_roller_races():
    # This fixture simulates the output of the get_high_roller_races function
    race1 = Race(race_id="R1", venue="Newmarket", race_time="14:30", race_number=1, is_handicap=False, number_of_runners=1, runners=[Runner(name="Horse A", odds=5.0)])
    setattr(race1, 'high_roller_score', 5.0)
    race2 = Race(race_id="R2", venue="Goodwood", race_time="14:45", race_number=2, is_handicap=False, number_of_runners=1, runners=[Runner(name="Horse C", odds=4.0)])
    setattr(race2, 'high_roller_score', 4.0)
    return [race1, race2]

@patch('paddock_parser.ui.terminal_ui.Table')
@patch('paddock_parser.ui.terminal_ui.Console')
def test_display_high_roller_report_uses_rich_table(MockConsole, MockTable, sample_high_roller_races):
    mock_console_instance = MockConsole()
    mock_table_instance = MockTable.return_value

    ui = TerminalUI(console=mock_console_instance)
    ui.display_high_roller_report(sample_high_roller_races)

    MockTable.assert_called_once_with(title="[bold green]High Roller Report[/bold green]")

    expected_calls = [
        call("Time", style="cyan"),
        call("Venue", style="magenta"),
        call("Favorite", style="green"),
        call("Odds", style="yellow")
    ]
    mock_table_instance.add_column.assert_has_calls(expected_calls, any_order=True)
    assert mock_table_instance.add_column.call_count == len(expected_calls)

    assert mock_table_instance.add_row.call_count == len(sample_high_roller_races)
    mock_table_instance.add_row.assert_any_call("14:30", "Newmarket", "Horse A", "5.00")
    mock_table_instance.add_row.assert_any_call("14:45", "Goodwood", "Horse C", "4.00")

    mock_console_instance.print.assert_called_once_with(mock_table_instance)

@patch('paddock_parser.ui.terminal_ui.Table')
@patch('paddock_parser.ui.terminal_ui.analyze_log_file')
@patch('paddock_parser.ui.terminal_ui.Console')
def test_display_log_analysis_report_uses_rich_table(MockConsole, MockAnalyze, MockTable):
    # Arrange
    mock_console_instance = MockConsole()
    mock_table_instance = MockTable.return_value
    mock_log_counts = {"INFO": 10, "WARNING": 2, "ERROR": 1}
    MockAnalyze.return_value = mock_log_counts
    ui = TerminalUI(console=mock_console_instance)

    # Act
    ui.display_log_analysis_report()

    # Assert
    MockAnalyze.assert_called_once()
    MockTable.assert_called_once_with(title="[bold blue]Log File Analysis[/bold blue]")

    expected_column_calls = [
        call("Log Level", style="cyan"),
        call("Count", style="magenta", justify="right"),
    ]
    mock_table_instance.add_column.assert_has_calls(expected_column_calls, any_order=False)

    expected_row_calls = [
        call("ERROR", "1"),
        call("INFO", "10"),
        call("WARNING", "2"),
    ]
    mock_table_instance.add_row.assert_has_calls(expected_row_calls, any_order=True)
    assert mock_table_instance.add_row.call_count == len(mock_log_counts)

    mock_console_instance.print.assert_called_with(mock_table_instance)


@pytest.mark.anyio
@patch('paddock_parser.ui.terminal_ui.get_high_roller_races')
@patch('paddock_parser.ui.terminal_ui.run_pipeline')
@patch('paddock_parser.ui.terminal_ui.TerminalUI.display_high_roller_report')
@patch('paddock_parser.ui.terminal_ui.Console')
async def test_run_high_roller_report_uses_rich_status(
    MockConsole, MockDisplay, MockRunPipeline, MockGetHighRoller, sample_high_roller_races
):
    # Setup mocks
    mock_console_instance = MockConsole()

    # Configure run_pipeline mock to return a value to prevent early exit
    async def mock_pipeline(*args, **kwargs):
        return [NormalizedRace(race_id="D1", track_name="Dummy", race_number=1, post_time=datetime.now(), runners=[NormalizedRunner(name="DummyHorse", program_number=1, odds=10.0)])]
    MockRunPipeline.side_effect = mock_pipeline

    MockGetHighRoller.return_value = sample_high_roller_races

    ui = TerminalUI(console=mock_console_instance)

    # Run the async method
    await ui._run_high_roller_report()

    # Assertions
    mock_console_instance.status.assert_called_once_with("Fetching data from providers...", spinner="dots")
    MockRunPipeline.assert_called_once()
    MockGetHighRoller.assert_called_once()
    MockDisplay.assert_called_once_with(sample_high_roller_races)
