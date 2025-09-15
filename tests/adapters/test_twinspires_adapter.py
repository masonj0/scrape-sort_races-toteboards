import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.paddock_parser.adapters.twinspires_adapter import TwinSpiresAdapter
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

@pytest.fixture
def mock_race_detail_html():
    """Loads the mock TwinSpires race detail HTML content."""
    fixture_path = Path(__file__).parent / "mock_data" / "twinspires_race_detail.html"
    return fixture_path.read_text()

@pytest.fixture
def mock_todays_tracks_html():
    """Loads the mock TwinSpires 'Today's Tracks' HTML content."""
    fixture_path = Path(__file__).parent / "mock_data" / "twinspires_todays_tracks.html"
    return fixture_path.read_text()

def test_twinspires_adapter_parse_single_race(mock_race_detail_html):
    """
    Tests that the _parse_single_race_detail helper method correctly
    parses a single race detail page into a NormalizedRace object.
    """
    # 1. Setup
    adapter = TwinSpiresAdapter()

    # 2. Execution
    # We are testing the internal helper method directly
    parsed_race = adapter._parse_single_race_detail(mock_race_detail_html)

    # 3. Assertions
    assert isinstance(parsed_race, NormalizedRace)
    assert parsed_race.track_name == "Churchill Downs"
    assert parsed_race.race_number == 1
    # The third runner "Scratched Runner" has invalid odds and should be skipped
    assert parsed_race.number_of_runners == 2
    assert len(parsed_race.runners) == 2

    # --- Detailed assertions for the first runner ---
    first_runner = parsed_race.runners[0]
    assert isinstance(first_runner, NormalizedRunner)
    assert first_runner.name == "Mighty Steed"
    assert first_runner.program_number == 1
    # Odds are "5/2" -> (5/2) + 1.0 = 3.5
    assert first_runner.odds == 3.5

    # --- Detailed assertions for the second runner ---
    second_runner = parsed_race.runners[1]
    assert second_runner.name == "Galloping Power"
    assert second_runner.program_number == 2
    # Odds are "10" -> 10.0 + 1.0 = 11.0
    assert second_runner.odds == 11.0

@pytest.mark.anyio
@patch('src.paddock_parser.adapters.twinspires_adapter.get_page_content', new_callable=AsyncMock)
async def test_twinspires_adapter_fetch_full_process(mock_get_page_content, mock_todays_tracks_html, mock_race_detail_html):
    """
    Tests the full two-stage fetch process of the TwinSpiresAdapter.
    """
    # 1. Setup
    # The first call to get_page_content should return the index page.
    # Subsequent calls should return the detail page for each link found.
    mock_get_page_content.side_effect = [
        mock_todays_tracks_html,
        mock_race_detail_html,
        mock_race_detail_html,
        mock_race_detail_html
    ]
    adapter = TwinSpiresAdapter()

    # 2. Execution
    fetched_races = await adapter.fetch()

    # 3. Assertions
    # The mock index page has 3 valid race links.
    # So, get_page_content should be called 4 times (1 for index + 3 for details).
    assert mock_get_page_content.call_count == 4

    # The mock detail page has 2 valid runners. Since we return the same detail
    # page for all 3 links, we expect 3 identical race objects.
    assert len(fetched_races) == 3
    assert fetched_races[0].track_name == "Churchill Downs"
    assert fetched_races[0].number_of_runners == 2
