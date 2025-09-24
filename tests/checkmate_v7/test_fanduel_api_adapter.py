import pytest
import json
import os
from unittest.mock import MagicMock, call

from src.checkmate_v7.adapters.fanduel import FanDuelApiAdapterV7
from src.checkmate_v7.base import DefensiveFetcher

# Determine the absolute path to the fixture files
SCHEDULE_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'fanduel_schedule_response.json')
DETAIL_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'fanduel_detail_response.json')


@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return MagicMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the FanDuelApiAdapterV7."""
    return FanDuelApiAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_schedule_response():
    """Reads the mock schedule JSON content from the fixture file."""
    with open(SCHEDULE_FIXTURE_PATH, 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_detail_response():
    """Reads the mock detail JSON content from the fixture file."""
    with open(DETAIL_FIXTURE_PATH, 'r') as f:
        return json.load(f)

def test_parse_races_with_populated_data(adapter, mock_schedule_response):
    """
    Tests that the adapter can successfully parse race schedule
    from the mock API JSON response.
    """
    # When
    parsed_races = adapter._parse_races(mock_schedule_response)

    # Then
    assert len(parsed_races) == 2

    race1 = parsed_races[0]
    assert race1.race_id == "66268"
    assert race1.track_name == "Finger Lakes"
    assert race1.race_number == 8
    assert len(race1.runners) == 0 # No runners in this response

def test_parse_races_with_empty_data(adapter):
    """
    Tests that the adapter's parse method can handle an empty (but valid) response.
    """
    # Given an empty API response
    empty_response = {"data": {"scheduleRaces": []}}

    # When
    parsed_races = adapter._parse_races(empty_response)

    # Then
    assert parsed_races == []

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_schedule_response):
    """
        Tests the end-to-end flow of the fetch_races method, mocking the single post call.
    """
    # Given
    mock_fetcher.post.return_value = mock_schedule_response

    # When
    races = adapter.fetch_races()

    # Then
    assert mock_fetcher.post.call_count == 1

    # Check the call arguments
    schedule_call_args = mock_fetcher.post.call_args_list[0]
    assert "GetRacingSchedule" in schedule_call_args.kwargs['json_data']['query']

    # Assert the parsing logic produced the expected number of races
    assert len(races) == 2
