import pytest
import os
from unittest.mock import AsyncMock
from src.checkmate_v7.services import BetfairDataScientistAdapterV7, DefensiveFetcher

# Determine the absolute path to the fixture file
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'betfair_data.csv')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the BetfairDataScientistAdapterV7."""
    return BetfairDataScientistAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_csv_content():
    """Reads the mock CSV content from the fixture file."""
    with open(FIXTURE_PATH, 'r') as f:
        return f.read()

def test_parse_races(adapter, mock_csv_content):
    """
    Tests that the adapter can successfully parse races and runners
    from the mock CSV data.
    """
    # When
    parsed_races = adapter._parse_races(mock_csv_content)

    # Then
    assert len(parsed_races) == 2

    # --- Test Race 1 (market_id 1.123) ---
    # The order is not guaranteed, so we find the race by its ID
    race1 = next((r for r in parsed_races if r.race_id == "1.123"), None)
    assert race1 is not None
    assert race1.track_name == "Unknown"
    assert len(race1.runners) == 3

    # Check runner details
    assert race1.runners[0].name == "1001"
    assert race1.runners[0].odds == 1.5
    assert race1.runners[2].name == "1003"
    assert race1.runners[2].odds == 10.0

    # --- Test Race 2 (market_id 1.456) ---
    race2 = next((r for r in parsed_races if r.race_id == "1.456"), None)
    assert race2 is not None
    assert len(race2.runners) == 2
    assert race2.runners[1].name == "2002"
    assert race2.runners[1].odds == 4.5

@pytest.mark.anyio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_csv_content):
    """
    Tests the end-to-end flow of the fetch_races method.
    """
    # Given
    mock_fetcher.fetch.return_value = mock_csv_content

    # When
    races = await adapter.fetch_races()

    # Then
    mock_fetcher.fetch.assert_called_once()
    assert "betfair-data-supplier.herokuapp.com" in mock_fetcher.fetch.call_args[0][0]

    # Assert the parsing logic produced the expected number of races
    assert len(races) == 2
    race1 = next((r for r in races if r.race_id == "1.123"), None)
    assert len(race1.runners) == 3
