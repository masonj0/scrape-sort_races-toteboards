import pytest
import os
from unittest.mock import AsyncMock
from src.checkmate_v7.services import TwinspiresAdapterV7, DefensiveFetcher

# Determine absolute paths to the fixture files
INDEX_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'twinspires_index.html')
DETAIL_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'twinspires_race_detail.html')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the TwinspiresAdapterV7."""
    return TwinspiresAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def index_html():
    """Reads the mock index HTML content from the fixture file."""
    with open(INDEX_FIXTURE_PATH, 'r') as f:
        return f.read()

@pytest.fixture
def detail_html():
    """Reads the mock race detail HTML content from the fixture file."""
    with open(DETAIL_FIXTURE_PATH, 'r') as f:
        return f.read()

def test_parse_race_links(adapter, index_html):
    """Tests that the adapter can parse the index page for race links correctly."""
    links = adapter._parse_race_links(index_html)

    # Should find 2 unique links, ignoring the results link and the duplicate
    assert len(links) == 2
    assert "https://www.twinspires.com/adw/todays-tracks/churchill-downs/2025-09-15/races/5/race-card" in links
    assert "https://www.twinspires.com/adw/todays-tracks/santa-anita/2025-09-15/races/8/race-card" in links

def test_parse_single_race_detail(adapter, detail_html):
    """Tests that the adapter can parse runners from a detail page."""
    race = adapter._parse_single_race_detail(detail_html)

    assert race is not None
    assert race.track_name == "Churchill Downs"
    assert race.race_number == 5

    # "No Odds Horse" and "Bad Odds Horse" should be skipped
    assert len(race.runners) == 2
    assert race.runners[0].name == "War Admiral"
    assert race.runners[0].program_number == 1
    assert race.runners[0].odds == 3.5 # 5/2 + 1

    assert race.runners[1].name == "Affirmed"
    assert race.runners[1].program_number == 2
    assert race.runners[1].odds == 4.0 # 3/1 + 1

@pytest.mark.asyncio
async def test_fetch_races_two_step(adapter, mock_fetcher, index_html, detail_html):
    """
    Tests the full two-step fetch process, mocking both API calls.
    """
    # Given: A more specific side effect for the mock fetcher
    async def fetch_side_effect(url, response_type='text'):
        if "?sortOrder=nextUp" in url:
            return index_html  # This is unique to the index page URL
        else:
            return detail_html    # Assume any other call is for a detail page

    mock_fetcher.fetch.side_effect = fetch_side_effect

    # When
    races = await adapter.fetch_races()

    # Then
    # Should have been called 3 times: 1 for index + 2 for details
    assert mock_fetcher.fetch.call_count == 3

    # Check that the final race objects are correctly populated
    assert len(races) == 2

    # Both races will have the same runners because we return the same detail page
    assert races[0].runners[0].name == "War Admiral"
    assert races[1].runners[1].name == "Affirmed"
