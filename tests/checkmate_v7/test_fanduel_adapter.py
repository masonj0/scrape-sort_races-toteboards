import pytest
import json
import os
from unittest.mock import AsyncMock
from src.checkmate_v7.services import FanDuelGraphQLAdapterV7, DefensiveFetcher

# Determine the absolute path to the fixture file
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'fanduel_graphql_response.json')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the FanDuelGraphQLAdapterV7."""
    return FanDuelGraphQLAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_graphql_response():
    """Reads the mock JSON content from the fixture file."""
    with open(FIXTURE_PATH, 'r') as f:
        return json.load(f)

def test_parse_races(adapter, mock_graphql_response):
    """
    Tests that the adapter can successfully parse races and runners
    from the mock GraphQL JSON response.
    """
    # When
    parsed_races = adapter._parse_races(mock_graphql_response)

    # Then
    assert len(parsed_races) == 2

    # --- Test Race 1 ---
    race1 = parsed_races[0]
    assert race1.track_name == "Saratoga"
    assert race1.race_number == 5
    # Check that the scratched runner was skipped
    assert len(race1.runners) == 2

    # Check runner details
    assert race1.runners[0].name == "Secretariat"
    assert race1.runners[0].odds == 3.0  # 2/1 + 1
    assert race1.runners[1].name == "Man o' War"
    assert race1.runners[1].odds == 6.0  # 5/1 + 1

    # --- Test Race 2 ---
    race2 = parsed_races[1]
    assert race2.track_name == "Belmont Park"
    assert len(race2.runners) == 1
    assert race2.runners[0].name == "Seabiscuit"
    assert race2.runners[0].odds == 1.5 # 1/2 + 1

@pytest.mark.anyio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_graphql_response):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the post call.
    """
    # Given
    # Configure the mock fetcher to return the mock JSON
    mock_fetcher.post.return_value = mock_graphql_response

    # When
    races = await adapter.fetch_races()

    # Then
    mock_fetcher.post.assert_called_once()
    assert "query AllRaces" in mock_fetcher.post.call_args[1]['json_data']['query']

    # Assert the parsing logic produced the expected number of races and runners
    assert len(races) == 2
    assert len(races[0].runners) == 2
    assert races[1].runners[0].name == "Seabiscuit"
