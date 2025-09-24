import pytest
import json
import os
from unittest.mock import AsyncMock
from src.checkmate_v7.adapters.pointsbet_adapter import PointsBetAdapter
from src.checkmate_v7.base import DefensiveFetcher

# Determine the absolute path to the fixture file
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'pointsbet_races.json')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the PointsBetAdapterV7."""
    return PointsBetAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_json_content():
    """Reads the mock JSON content from the fixture file."""
    with open(FIXTURE_PATH, 'r') as f:
        return json.load(f)

def test_parse_races_with_runners(adapter, mock_json_content):
    """
    Tests that the adapter can successfully parse races including runners
    from the mock JSON fixture.
    """
    # When
    parsed_races = adapter._parse_races(mock_json_content.get('events', []))

    # Then
    # The second race in the fixture has no runners, so only 1 should be parsed.
    assert len(parsed_races) == 1

    race = parsed_races[0]
    assert race.race_id == "PB_R_12345"
    assert race.track_name == "Flemington"
    assert race.race_number == 7

    # All 4 runners should be parsed as they have a runnerNumber
    assert len(race.runners) == 4

    # Check details of the parsed runners
    assert race.runners[0].name == "Lightning Bolt"
    assert race.runners[0].program_number == 1
    assert race.runners[0].odds == 3.50

    assert race.runners[1].name == "Steady Eddie"
    assert race.runners[1].program_number == 2
    assert race.runners[1].odds == 8.00

    # This runner has no odds, but should still be included
    assert race.runners[2].name == "No Show"
    assert race.runners[2].program_number == 3
    assert race.runners[2].odds is None

    assert race.runners[3].name == "Just Happy To Be Here"
    assert race.runners[3].program_number == 4
    assert race.runners[3].odds == 51.00

@pytest.mark.anyio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_json_content):
    """
    Tests the end-to-end flow of the fetch_races method using the detailed fixture.
    """
    # Given
    # Configure the mock fetcher to return the mock JSON as a string
    mock_fetcher.fetch.return_value = json.dumps(mock_json_content)

    # When
    races = await adapter.fetch_races()

    # Then
    mock_fetcher.fetch.assert_called_once_with(adapter.API_URL)

    # Assert the parsing logic produced the expected race and runners
    assert len(races) == 1
    assert len(races[0].runners) == 4
    assert races[0].runners[0].name == "Lightning Bolt"
