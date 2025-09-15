import pytest
import os
import json
from unittest.mock import AsyncMock
from src.checkmate_v7.services import RacingPostAdapterV7, DefensiveFetcher

# Determine the absolute path to the fixture file
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'racingpost_racecard.html')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the RacingPostAdapterV7."""
    return RacingPostAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_html_content():
    """Reads the mock HTML content from the fixture file."""
    with open(FIXTURE_PATH, 'r') as f:
        return f.read()

def test_parse_races_with_runners(adapter, mock_html_content):
    """
    Tests that the adapter can successfully parse a race including its runners
    from the mock fixture file.
    """
    # When
    parsed_races = adapter._parse_races(mock_html_content)

    # Then
    assert len(parsed_races) == 1

    race = parsed_races[0]
    assert race.race_id == "rp_12345"
    assert race.track_name == "Newmarket"

    # Check that the disabled runner was skipped
    assert len(race.runners) == 3

    # Check details of the parsed runners
    assert race.runners[0].name == "Speedy Gonzales"
    assert race.runners[0].program_number == 1

    assert race.runners[1].name == "Slow Poke"
    assert race.runners[1].program_number == 2

    assert race.runners[2].name == "Just a Horse"
    assert race.runners[2].program_number == 4

@pytest.mark.asyncio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_html_content):
    """
    Tests the end-to-end flow of the fetch_races method using the detailed fixture.
    """
    # Given a mock URL
    mock_url = "https://www.racingpost.com/some-race"
    # Configure the mock fetcher to return the mock HTML
    mock_fetcher.fetch.return_value = mock_html_content

    # When
    races = await adapter.fetch_races(url=mock_url)

    # Then
    mock_fetcher.fetch.assert_called_once_with(mock_url)

    # Assert the parsing logic produced the expected race and runners
    assert len(races) == 1
    assert len(races[0].runners) == 3
    assert races[0].runners[0].name == "Speedy Gonzales"
