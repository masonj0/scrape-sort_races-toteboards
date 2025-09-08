"""
Test-as-Spec for Terminal UI Module
Path: tests/ui/test_terminal_ui.py
"""

from unittest.mock import Mock, patch, call
from datetime import datetime

# Assume these data structures will be imported from the project
from paddock_parser.base import NormalizedRace


class TestTerminalUIInitialization:
    @patch('src.paddock_parser.ui.terminal_ui.Console')
    def test_terminal_ui_can_be_initialized(self, mock_console_class):
        from src.paddock_parser.ui.terminal_ui import TerminalUI
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        terminal_ui = TerminalUI()

        assert terminal_ui is not None
        mock_console_class.assert_called_once()
        assert terminal_ui.console == mock_console

class TestDynamicRaceTable:
    @patch('src.paddock_parser.ui.terminal_ui.Table')
    def test_display_races_creates_table_with_correct_headers(self, mock_table_class):
        from src.paddock_parser.ui.terminal_ui import TerminalUI
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        terminal_ui = TerminalUI(console=Mock())
        terminal_ui.display_races([])

        mock_table_class.assert_called_once_with(title="Race Information")
        expected_headers = ["Track", "Race #", "Post Time", "Runners", "Score"]
        header_calls = mock_table.add_column.call_args_list

        assert len(header_calls) == len(expected_headers)
        for i, expected_header in enumerate(expected_headers):
            assert header_calls[i] == call(expected_header, justify="left")

    @patch('src.paddock_parser.ui.terminal_ui.Table')
    def test_display_races_adds_correct_rows(self, mock_table_class):
        from src.paddock_parser.ui.terminal_ui import TerminalUI
        mock_table = Mock()
        mock_table_class.return_value = mock_table
        terminal_ui = TerminalUI(console=Mock())

        races = [
            NormalizedRace(race_id="C1", track_name="Churchill", race_number=1, post_time=datetime(2025, 9, 1, 14, 30), number_of_runners=8, score=85),
            NormalizedRace(race_id="B3", track_name="Belmont", race_number=3, post_time=None, number_of_runners=12, score=None)
        ]

        terminal_ui.display_races(races)

        assert mock_table.add_row.call_count == 2
        row_calls = mock_table.add_row.call_args_list
        assert call("Churchill", "1", "14:30", "8", "85") in row_calls
        assert call("Belmont", "3", "N/A", "12", "N/A") in row_calls

class TestProgressBarFunctionality:
    @patch('src.paddock_parser.ui.terminal_ui.Progress')
    def test_progress_bar_workflow(self, mock_progress_class):
        from src.paddock_parser.ui.terminal_ui import TerminalUI
        mock_progress = Mock()
        mock_progress_class.return_value = mock_progress
        mock_task_id = "task_123"
        mock_progress.add_task.return_value = mock_task_id

        terminal_ui = TerminalUI(console=Mock())
        num_tasks = 5

        terminal_ui.start_fetching_progress(num_tasks)
        mock_progress_class.assert_called_once()
        mock_progress.start.assert_called_once()
        mock_progress.add_task.assert_called_once_with("Fetching races...", total=num_tasks)

        terminal_ui.update_fetching_progress()
        mock_progress.update.assert_called_once_with(mock_task_id, advance=1)

        terminal_ui.stop_fetching_progress()
        mock_progress.stop.assert_called_once()
        assert terminal_ui.progress is None

class TestLoggingIntegration:
    @patch('src.paddock_parser.ui.terminal_ui.RichHandler')
    def test_setup_logging_creates_handler(self, mock_rich_handler_class):
        from src.paddock_parser.ui.terminal_ui import TerminalUI
        terminal_ui = TerminalUI(console=Mock())
        terminal_ui.setup_logging()

        mock_rich_handler_class.assert_called_once()
        assert terminal_ui.log_handler is not None


@patch('src.paddock_parser.ui.terminal_ui.Console')
def test_display_high_roller_report_shows_info_when_empty(MockConsole):
    # Arrange
    from src.paddock_parser.ui.terminal_ui import TerminalUI
    mock_console_instance = MockConsole.return_value
    ui = TerminalUI()
    # Act
    ui.display_high_roller_report([])
    # Assert
    mock_console_instance.print.assert_called_once()
    actual_output = mock_console_instance.print.call_args[0][0]
    assert "No races met the High Roller criteria." in actual_output
    assert "next 25 minutes" in actual_output
    assert "Fewer than 7" in actual_output
