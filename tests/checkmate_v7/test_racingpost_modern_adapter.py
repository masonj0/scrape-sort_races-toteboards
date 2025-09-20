import pytest
import os
from unittest.mock import AsyncMock

from src.checkmate_v7.adapters.racingpost_adapter import RacingPostModernAdapter
from src.checkmate_v7.base import DefensiveFetcher

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the new RacingPostModernAdapter."""
    return RacingPostModernAdapter(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_html_data():
    """Reads the mock HTML content from the fixture file."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', 'racingpost_racecard.html')
    with open(path, 'r') as f:
        return f.read()

# --- Unit Tests ---

def test_parse_races(adapter, mock_html_data):
    """Tests that the adapter correctly parses the HTML racecard data."""
    # When
    races = adapter._parse_races(mock_html_data)

    # Then
    assert len(races) == 1

    race = races[0]
    assert race.race_id == "rp_12345"
    assert race.track_name == "Newmarket"

    # Check that the non-runner was skipped
    assert len(race.runners) == 3

    assert race.runners[0].name == "Speedy Gonzales"
    assert race.runners[0].program_number == 1

    assert race.runners[1].name == "Slow Poke"
    assert race.runners[1].program_number == 2

    assert race.runners[2].name == "Just a Horse"
    assert race.runners[2].program_number == 4

@pytest.mark.anyio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_html_data):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the fetcher call.
    """
    # Given
    mock_fetcher.fetch.return_value = mock_html_data

    # When
    races = await adapter.fetch_races()

    # Then
    mock_fetcher.fetch.assert_called_once_with("https://www.racingpost.com/racecards/", response_type='text')

    assert len(races) == 1
    assert len(races[0].runners) == 3
    assert races[0].runners[0].name == "Speedy Gonzales"
