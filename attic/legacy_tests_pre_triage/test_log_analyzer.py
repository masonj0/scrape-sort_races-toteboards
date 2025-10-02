import pytest
from pathlib import Path
from src.paddock_parser.log_analyzer import analyze_log_file

@pytest.fixture
def sample_log_file(tmp_path: Path) -> Path:
    """Creates a temporary log file with sample content."""
    log_content = """
2025-09-08 10:00:00 - INFO - --- Paddock Parser NG Pipeline Start ---
2025-09-08 10:00:01 - INFO - Running adapter: skysports...
2025-09-08 10:00:02 - DEBUG - Fetching URL: https://www.skysports.com/greyhound-racing/racecards
2025-09-08 10:00:03 - INFO - Parsed 5 races from skysports.
2025-09-08 10:00:04 - INFO - Running adapter: attheraces...
2025-09-08 10:00:05 - WARNING - No races found for attheraces.
2025-09-08 10:00:06 - INFO - Running adapter: fanduel...
2025-09-08 10:00:07 - ERROR - An error occurred in the 'fanduel' adapter. See details below.
Traceback (most recent call last):
  File "src/paddock_parser/pipeline.py", line 145, in run_pipeline
    normalized_races = adapter.parse_data(raw_data)
KeyError: 'races'
2025-09-08 10:00:08 - CRITICAL - Pipeline failure. Cannot continue.
2025-09-08 10:00:09 - DEBUG - Some other debug message.
"""
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)
    return log_file

def test_analyze_log_file_with_sample_data(sample_log_file: Path):
    """
    SPEC: Must correctly count log levels from a typical log file.
    """
    # Act
    counts = analyze_log_file(str(sample_log_file))

    # Assert
    assert counts == {
        "INFO": 5,
        "DEBUG": 2,
        "WARNING": 1,
        "ERROR": 1,
        "CRITICAL": 1,
    }

def test_analyze_log_file_non_existent_file():
    """
    SPEC: Must return an empty dictionary if the log file does not exist.
    """
    # Act
    counts = analyze_log_file("non_existent_file.log")

    # Assert
    assert counts == {}

def test_analyze_log_file_empty_file(tmp_path: Path):
    """
    SPEC: Must return an empty dictionary for an empty log file.
    """
    # Arrange
    empty_log_file = tmp_path / "empty.log"
    empty_log_file.write_text("")

    # Act
    counts = analyze_log_file(str(empty_log_file))

    # Assert
    assert counts == {}

def test_analyze_log_file_with_no_log_levels(tmp_path: Path):
    """
    SPEC: Must return an empty dictionary if the file contains no recognizable log levels.
    """
    # Arrange
    no_levels_file = tmp_path / "no_levels.log"
    no_levels_file.write_text("This is a line.\nSo is this.\nAnd another one.")

    # Act
    counts = analyze_log_file(str(no_levels_file))

    # Assert
    assert counts == {}
