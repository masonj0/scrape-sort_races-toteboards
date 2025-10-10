import pytest
from pathlib import Path
from unittest.mock import patch
import sys
from src.paddock_parser.adapters.timeform_adapter import TimeformAdapter

@pytest.fixture
def mock_html():
    path = Path(__file__).parent / "timeform.html"
    return path.read_text()

@pytest.fixture
def mock_race_detail_html():
    path = Path(__file__).parent / "mock_data" / "timeform_race_detail_sample.html"
    return path.read_text()

@pytest.mark.anyio
@patch("src.paddock_parser.adapters.timeform_adapter.ForagerClient.fetch")
async def test_fetch(mock_fetch, mock_html, mock_race_detail_html):
    """
    Tests the full end-to-end fetch and parse process for TimeformAdapter.
    """
    if 'trio' in sys.modules:
        pytest.skip("Skipping timeform test on trio due to potential event loop conflicts.")

    # The first call to fetch will be for the index page.
    # The subsequent 35 calls will be for the race detail pages.
    mock_fetch.side_effect = [mock_html] + ([mock_race_detail_html] * 35)

    adapter = TimeformAdapter()
    races = await adapter.fetch()

    assert mock_fetch.call_count == 36
    assert len(races) == 35

    # Check a sample race from the mocked detail pages
    a_race = races[0]
    assert a_race.track_name == "HAYDOCK PARK"
    assert a_race.number_of_runners == 9
    assert len(a_race.runners) == 9

    co_runner = next((r for r in a_race.runners if r.name == "COMMANDING OFFICER (GER)"), None)
    assert co_runner is not None
    assert co_runner.program_number == 2
    assert co_runner.odds == pytest.approx(10/3 + 1)

def test_extract_race_links(mock_html):
    adapter = TimeformAdapter()
    links = adapter._extract_race_links(mock_html)
    assert len(links) == 35
    assert "https://www.timeform.com/horse-racing/racecards/haydock-park/2025-09-04/1430/22/2/mccoys-racing-lounge-ebf-novice-stakes" in links

def test_parse_race_details(mock_race_detail_html):
    adapter = TimeformAdapter()
    race = adapter.parse_race_details(mock_race_detail_html, "http://example.com")

    assert race is not None
    assert race.track_name == "HAYDOCK PARK"
    assert race.number_of_runners == 9
    assert len(race.runners) == 9

    co_runner = next((r for r in race.runners if r.name == "COMMANDING OFFICER (GER)"), None)
    assert co_runner is not None
    assert co_runner.program_number == 2
    assert co_runner.odds == pytest.approx(10/3 + 1)
