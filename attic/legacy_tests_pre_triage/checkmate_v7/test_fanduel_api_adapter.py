import pytest
import json
import os
from unittest.mock import MagicMock

from src.checkmate_v7.adapters.AndWereOff import FanDuelApiAdapter as FanDuelApiAdapterV7
from src.checkmate_v7.base import DefensiveFetcher

# Determine the absolute path to the fixture files
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "fanduel")

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Provides a MagicMock for the DefensiveFetcher."""
    return MagicMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Provides an adapter instance with a mocked fetcher."""
    return FanDuelApiAdapterV7(mock_fetcher)

@pytest.fixture
def mock_schedule_response():
    """Provides a mock API response for the race schedule."""
    with open(os.path.join(FIXTURE_PATH, "schedule.json"), "r") as f:
        return json.load(f)

# --- Tests ---

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_schedule_response):
    """
        Tests the end-to-end flow of the fetch_races method, mocking the single post call.
    """
    # Given
    mock_fetcher.post.return_value = mock_schedule_response

    # When
    races = adapter.fetch_races()

    # Then
    mock_fetcher.post.assert_called_once()

    # Check the call arguments
    schedule_call_args = mock_fetcher.post.call_args_list[0]
    assert "GetRacingSchedule" in schedule_call_args.kwargs['json_data']['query']

    # Assert the parsing logic produced the expected number of races
    assert len(races) == 2
    assert races[0].race_id == "66268"
    assert len(races[0].runners) == 8
    assert races[1].race_id == "66269"
    assert len(races[1].runners) == 7
    assert races[0].runners[0].name == "Strong Odor"
    assert races[0].runners[0].program_number == 1