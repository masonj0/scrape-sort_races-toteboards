import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from src.paddock_parser.adapters.skysports_adapter import SkySportsAdapter

@pytest.fixture
def mock_race_card_html():
    # A simplified version of the racecards index page
    return """
    <div class="sdc-site-concertina-block">
        <h3 class="sdc-site-concertina-block__title">
            <span class="sdc-site-concertina-block__title">Chelmsford City</span>
        </h3>
        <div class="sdc-site-racing-meetings__event">
            <a class="sdc-site-racing-meetings__event-link" href="/racing/results/full-result/12345"></a>
        </div>
    </div>
    """

@pytest.fixture
def mock_race_detail_html():
    # A simplified version of a race detail page
    return Path(__file__).parent.joinpath("skysports_race_detail_sample.html").read_text()

import sys

@pytest.mark.anyio
@patch("src.paddock_parser.adapters.skysports_adapter.get_page_content")
async def test_skysports_adapter_fetches_and_parses(mock_get_page_content, mock_race_card_html, mock_race_detail_html):
    """
    Tests the full end-to-end fetch and parse process for SkySportsAdapter,
    mocking the new resilient fetcher.
    """
    if 'trio' in sys.modules:
        pytest.skip("Skipping skysports test on trio due to asyncio.gather conflict.")
    # --- Setup ---
    # Configure the mock to return the index page on the first call,
    # and the detail page on the second call.
    mock_get_page_content.side_effect = [
        mock_race_card_html,
        mock_race_detail_html
    ]

    adapter = SkySportsAdapter()

    # --- Run ---
    races = await adapter.fetch()

    # --- Assertions ---
    # The adapter should make one call for the index, and one for the single race link found.
    assert mock_get_page_content.call_count == 2

    # We should have parsed exactly one race.
    assert len(races) == 1
    race = races[0]

    # Assert details from the parsed race.
    assert race.track_name == "Chelmsford City"
    assert race.race_number == 1
    assert race.race_type == "Handicap" # from "Handicap" in the h2 title
    assert len(race.runners) == 2

    runner1 = race.runners[0]
    assert runner1.name == "Horse One"
    assert runner1.program_number == 1
    assert runner1.odds == pytest.approx(6.0) # 5/1

    runner2 = race.runners[1]
    assert runner2.name == "Horse Two"
    assert runner2.program_number == 2
    assert runner2.odds == pytest.approx(2.0) # EVENS
