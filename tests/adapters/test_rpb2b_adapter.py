import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.paddock_parser.adapters.rpb2b_adapter import Rpb2bAdapter
from src.paddock_parser.base import NormalizedRace, NormalizedRunner


@pytest.fixture
def mock_race_list_json():
    path = Path(__file__).parent / "mock_data" / "rpb2b_racecards_sample.json"
    return path.read_text()


@pytest.fixture
def mock_race_detail_json():
    path = Path(__file__).parent / "mock_data" / "rpb2b_race_detail_sample.json"
    return path.read_text()


@pytest.mark.anyio
@patch("src.paddock_parser.adapters.rpb2b_adapter.get_page_content")
async def test_rpb2b_adapter_fetches_and_parses(
    mock_get_page_content, mock_race_list_json, mock_race_detail_json
):
    """
    Tests the full end-to-end fetch and parse process for Rpb2bAdapter.
    """
    import sys
    if 'trio' in sys.modules:
        pytest.skip("Skipping rpb2b test on trio due to asyncio.gather conflict.")

    # Configure the mock to return different JSON based on the URL requested
    async def fetch_side_effect(url):
        if "daily" in url:
            return mock_race_list_json

        # For detail calls, return a slightly modified version of the sample
        # to make the test more robust.
        race_detail = json.loads(mock_race_detail_json)
        if "81650def-54b2-408c-991f-fbae800060b0" in url:
            race_detail["raceNumber"] = 1
            race_detail["results"]["result"][0]["startingPrice"] = "10/1"
        elif "4c459555-265e-4aa4-beaf-e82d8781c13d" in url:
            race_detail["raceNumber"] = 2
            race_detail["results"]["result"][0]["startingPrice"] = "5/1"
        return json.dumps(race_detail)

    mock_get_page_content.side_effect = fetch_side_effect

    adapter = Rpb2bAdapter()
    races = await adapter.fetch()

    assert mock_get_page_content.call_count > 1
    assert len(races) > 0

    # Test the first race
    race1 = next(
        (r for r in races if r.race_id == "81650def-54b2-408c-991f-fbae800060b0"), None
    )
    assert race1 is not None
    assert race1.track_name == "Parx"
    assert race1.race_number == 1
    assert race1.race_type == "Flat"
    assert race1.number_of_runners == 6
    assert race1.runners[0].odds == 11.0

    # Test the second race to ensure different data is processed
    race2 = next(
        (r for r in races if r.race_id == "4c459555-265e-4aa4-beaf-e82d8781c13d"), None
    )
    assert race2 is not None
    assert race2.track_name == "Parx"
    assert race2.race_number == 2
    assert race2.runners[0].odds == 6.0
