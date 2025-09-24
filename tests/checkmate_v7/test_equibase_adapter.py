import pytest
import os
from unittest.mock import AsyncMock
from src.checkmate_v7.adapters.equibase_adapter import EquibaseAdapter
from src.checkmate_v7.base import DefensiveFetcher
from src.checkmate_v7.models import Race

# Determine absolute paths to the fixture files
SCHEDULE_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'equibase_entries.html')
DETAIL_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'equibase_race_detail.html')

@pytest.fixture
def mock_fetcher():
    """Pytest fixture for a mock DefensiveFetcher."""
    return AsyncMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Pytest fixture for the EquibaseAdapterV7."""
    return EquibaseAdapterV7(defensive_fetcher=mock_fetcher)

@pytest.fixture
def schedule_html():
    """Reads the mock schedule HTML content from the fixture file."""
    with open(SCHEDULE_FIXTURE_PATH, 'r') as f:
        return f.read()

@pytest.fixture
def detail_html():
    """Reads the mock race detail HTML content from the fixture file."""
    with open(DETAIL_FIXTURE_PATH, 'r') as f:
        return f.read()

def test_parse_schedule(adapter, schedule_html):
    """Tests that the adapter can parse the main schedule page correctly."""
    partial_races, detail_urls = adapter._parse_race_schedule(schedule_html)

    assert len(partial_races) == 3
    assert len(detail_urls) == 3

    assert partial_races[0].track_name == "Aqueduct"
    assert partial_races[0].race_number == 1
    assert detail_urls[0] == "/entries/AQU/20250915/1"

    assert partial_races[2].track_name == "Gulfstream Park"
    assert partial_races[2].race_number == 8

def test_parse_runners_from_detail_page(adapter, detail_html):
    """Tests that the adapter can parse runners from a detail page."""
    runners = adapter._parse_runners_from_detail_page(detail_html)

    assert len(runners) == 3
    assert runners[0].name == "Gallant Fox"
    assert runners[0].program_number == 1
    assert runners[2].name == "Citation"
    assert runners[2].program_number == 3

@pytest.mark.anyio
async def test_fetch_races_two_step(adapter, mock_fetcher, schedule_html, detail_html):
    """
    Tests the full two-step fetch process, mocking both API calls.
    """
    # Given: A side effect for the mock fetcher to return different HTML
    # based on the URL being fetched.
    async def fetch_side_effect(url):
        if "ENT_" in url:
            return schedule_html  # It's the main schedule page
        else:
            return detail_html    # It's a race detail page

    mock_fetcher.fetch.side_effect = fetch_side_effect

    # When
    races = await adapter.fetch_races()

    # Then
    # Should have been called 4 times: 1 for schedule + 3 for details
    assert mock_fetcher.fetch.call_count == 4

    # Check that the final race objects are correctly populated
    assert len(races) == 3

    # The first race should have runners from the detail page
    assert races[0].track_name == "Aqueduct"
    assert len(races[0].runners) == 3
    assert races[0].runners[0].name == "Gallant Fox"

    # The third race should also have runners
    assert races[2].track_name == "Gulfstream Park"
    assert len(races[2].runners) == 3
    assert races[2].runners[1].name == "Zev"
