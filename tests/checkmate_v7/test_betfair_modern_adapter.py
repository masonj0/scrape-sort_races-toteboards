import pytest
import os
from unittest.mock import MagicMock

from src.checkmate_v7.adapters.betfair_data_scientist_adapter import BetfairModernAdapter
from src.checkmate_v7.base import DefensiveFetcher

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return MagicMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the new BetfairModernAdapter."""
    return BetfairModernAdapter(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_csv_data():
    """Reads the mock CSV content from the fixture file."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', 'betfair_data.csv')
    with open(path, 'r') as f:
        return f.read()

# --- Unit Tests ---

def test_parse_races(adapter, mock_csv_data):
    """Tests that the adapter correctly parses the CSV data."""
    # When
    races = adapter._parse_races(mock_csv_data)

    # Then
    assert len(races) == 2

    # Find the races by their ID for stable testing
    race1 = next((r for r in races if r.race_id == "1.123"), None)
    race2 = next((r for r in races if r.race_id == "1.456"), None)

    assert race1 is not None
    assert race2 is not None

    # --- Test Race 1 ---
    assert race1.track_name == "Unknown"
    assert len(race1.runners) == 3
    assert race1.runners[0].name == "1001"
    assert race1.runners[0].odds == 1.5
    assert race1.runners[1].name == "1002"
    assert race1.runners[1].odds == 3.2
    assert race1.runners[2].name == "1003"
    assert race1.runners[2].odds == 10.0

    # --- Test Race 2 ---
    assert race2.track_name == "Unknown"
    assert len(race2.runners) == 2
    assert race2.runners[0].name == "2001"
    assert race2.runners[0].odds == 2.0
    assert race2.runners[1].name == "2002"
    assert race2.runners[1].odds == 4.5

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_csv_data):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the fetcher call.
    """
    # Given
    mock_fetcher.fetch.return_value = mock_csv_data

    # When
    races = adapter.fetch_races()

    # Then
    mock_fetcher.fetch.assert_called_once()
    assert "presenter=RatingsPresenter" in mock_fetcher.fetch.call_args[0][0]

    assert len(races) == 2
    race1 = next((r for r in races if r.race_id == "1.123"), None)
    assert race1 is not None
    assert len(race1.runners) == 3
