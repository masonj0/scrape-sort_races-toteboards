import pytest
from unittest.mock import AsyncMock, call

from src.checkmate_v7.adapters.twinspires_adapter import TwinspiresModernAdapter
from src.checkmate_v7.base import DefensiveFetcher
import os

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the new TwinspiresModernAdapter."""
    return TwinspiresModernAdapter(defensive_fetcher=mock_fetcher)

@pytest.fixture
def mock_index_html():
    """Reads the mock index HTML content from the fixture file."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', 'twinspires_index.html')
    with open(path, 'r') as f:
        return f.read()

@pytest.fixture
def mock_detail_html():
    """Reads the mock race detail HTML content from the fixture file."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', 'twinspires_race_detail.html')
    with open(path, 'r') as f:
        return f.read()

# --- Unit Tests ---

def test_parse_race_links(adapter, mock_index_html):
    """Tests that the adapter correctly parses race detail links from the index page."""
    # When
    links = adapter._parse_race_links(mock_index_html)
    # Then
    assert len(links) == 2
    assert "https://www.twinspires.com/adw/todays-tracks/churchill-downs/2025-09-15/races/5/race-card" in links
    assert "https://www.twinspires.com/adw/todays-tracks/santa-anita/2025-09-15/races/8/race-card" in links

def test_parse_single_race_detail(adapter, mock_detail_html):
    """Tests that the adapter correctly parses a single race detail page."""
    # When
    race = adapter._parse_single_race_detail(mock_detail_html)
    # Then
    assert race is not None
    assert race.track_name == "Churchill Downs"
    assert race.race_number == 5
    assert len(race.runners) == 2

    assert race.runners[0].name == "War Admiral"
    assert race.runners[0].odds == 3.5  # 5/2 -> 2.5 + 1.0
    assert race.runners[0].program_number == 1

    assert race.runners[1].name == "Affirmed"
    assert race.runners[1].odds == 4.0  # 3/1 -> 3.0 + 1.0
    assert race.runners[1].program_number == 2

@pytest.mark.anyio
async def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_index_html, mock_detail_html):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the fetcher calls.
    """
    # Given
    # The links that will be parsed from the index_html
    parsed_links = [
        "https://www.twinspires.com/adw/todays-tracks/churchill-downs/2025-09-15/races/5/race-card",
        "https://www.twinspires.com/adw/todays-tracks/santa-anita/2025-09-15/races/8/race-card"
    ]

    # Mock the fetcher to return the index page first, then the detail page for each subsequent call
    mock_fetcher.fetch.side_effect = [
        mock_index_html,
        mock_detail_html, # Corresponds to first link
        mock_detail_html  # Corresponds to second link
    ]

    # When
    races = await adapter.fetch_races()

    # Then
    # Check that the fetcher was called for the index and then for each parsed link
    assert mock_fetcher.fetch.call_count == 3
    mock_fetcher.fetch.assert_any_call("https://www.twinspires.com/adw/todays-tracks?sortOrder=nextUp", response_type='text')
    mock_fetcher.fetch.assert_any_call(parsed_links[0], response_type='text')
    mock_fetcher.fetch.assert_any_call(parsed_links[1], response_type='text')

    # Assert that the parsing logic produced the expected result
    assert len(races) == 2
    assert races[0].track_name == "Churchill Downs"
    assert races[1].track_name == "Churchill Downs" # Both calls used the same detail page fixture
    assert len(races[0].runners) == 2
