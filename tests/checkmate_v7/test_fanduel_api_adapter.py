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

def test_parse_races_with_populated_data(adapter, mock_schedule_response, mock_detail_response):
    """
    Tests that the adapter can successfully parse races and runners
    from the mock two-stage API JSON responses.
    """
    # When
    parsed_races = adapter._parse_races(mock_schedule_response, mock_detail_response)

    # Then
    assert len(parsed_races) == 1

    race1 = parsed_races[0]
    assert race1.race_id == "66268"
    assert race1.track_name == "Finger Lakes"
    assert race1.race_number == 8
    assert len(race1.runners) == 6

    # Check a couple of runner details
    assert race1.runners[0].name == "Bustin Stones"
    assert race1.runners[0].program_number == "1"
    assert race1.runners[0].jockey == "J. A. Gomez"
    assert race1.runners[0].trainer == "Linda K. Dixon"
    assert race1.runners[0].odds == 3.5 # (5/2) + 1

    assert race1.runners[5].name == "War of Thrones"
    assert race1.runners[5].program_number == "6"
    assert race1.runners[5].odds == 8.0 # (7/1) + 1

def test_parse_races_with_empty_data(adapter):
    """
    Tests that the adapter's parse method can handle an empty (but valid) response.
    """
    # Given an empty API response
    empty_response = {"data": {"scheduleRaces": []}}
    empty_detail_response = {"data": {"races": []}}

    # When
    parsed_races = adapter._parse_races(empty_response, empty_detail_response)

    # Then
    assert parsed_races == []

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_schedule_response, mock_detail_response):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the two post calls.
    """
    # Given
    # Configure the mock fetcher to return the mock JSON responses in order
    mock_fetcher.post.side_effect = [mock_schedule_response, mock_detail_response]

    # When
    races = adapter.fetch_races()

    # Then
    assert mock_fetcher.post.call_count == 2

    # Check the first call (schedule)
    schedule_call_args = mock_fetcher.post.call_args_list[0]
    assert "getLhnInfo" in schedule_call_args.kwargs['json_data']['query']

    # Check the second call (details)
    detail_call_args = mock_fetcher.post.call_args_list[1]
    assert "getGraphRaceBettingInterest" in detail_call_args.kwargs['json_data']['query']
    # Assert that the tvgRaceIds from the first call were passed to the second
    assert detail_call_args.kwargs['json_data']['variables']['tvgRaceIds'] == [12345, 67890]


    # Assert the parsing logic produced the expected number of races
    assert len(races) == 1
    assert races[0].track_name == "Finger Lakes"
