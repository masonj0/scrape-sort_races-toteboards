import pytest
import os
from unittest.mock import MagicMock

from src.checkmate_v7.adapters.AndWereOff import BetfairDataScientistAdapter as BetfairModernAdapter
from src.checkmate_v7.base import DefensiveFetcher

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Provides a MagicMock for the DefensiveFetcher."""
    return MagicMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Provides an adapter instance with a mocked fetcher."""
    return BetfairModernAdapter(mock_fetcher)

@pytest.fixture
def mock_csv_data():
    """Provides mock CSV data for race details."""
    return 'market_id,selection_id,meetings.races.runners.ratedPrice\n1.123,1001,1.5\n1.123,1002,3.2\n1.123,1003,10.0\n1.456,2001,2.0\n1.456,2002,4.5\n'

# --- Tests ---

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_csv_data):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the fetcher call.
    """
    # Given
    mock_fetcher.get.return_value = mock_csv_data

    # When
    races = adapter.fetch_races()

    # Then
    mock_fetcher.get.assert_called_once()
    assert len(races) == 2
    assert races[0].race_id == "1.123"
    assert len(races[0].runners) == 3
    assert races[1].race_id == "1.456"
    assert len(races[1].runners) == 2
    assert races[0].runners[0].name == "1001.0"
    assert races[0].runners[0].odds == 1.5