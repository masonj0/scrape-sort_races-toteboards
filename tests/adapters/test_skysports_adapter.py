import pytest
from pathlib import Path
from unittest.mock import patch
from paddock_parser.adapters.skysports_adapter import SkySportsAdapter

@pytest.mark.anyio
@patch("paddock_parser.http_client.ForagerClient.fetch")
async def test_skysports_adapter_fetches_and_parses(mock_fetch):
    """
    Tests the full end-to-end fetch and parse process for SkySportsAdapter,
    with the fetch mechanism mocked.
    """
    # --- Setup ---
    adapter = SkySportsAdapter()

    # Load the sample HTML from a fixture file for the test
    fixture_path = Path(__file__).parent / "skysports_racecards_sample.html"
    sample_html = fixture_path.read_text(encoding="utf-8")

    # Configure the mock to return our sample HTML
    # Since the mocked function is async, the mock's return value will be awaited
    mock_fetch.return_value = sample_html

    # --- Run ---
    # Run the fetch method, which will use the mocked fetch_html_content
    races = await adapter.fetch()

    # --- Assertions ---
    assert races is not None
    assert len(races) == 113

    # Find a specific, known race in the results for a deep check
    target_race = None
    for race in races:
        if race.track_name == "Chelmsford City" and race.post_time and race.post_time.strftime("%H:%M") == "14:20":
            target_race = race
            break

    assert target_race is not None, "Could not find the target Chelmsford City 14:20 race"
    assert target_race.race_number == 1
    assert target_race.number_of_runners == 8
    # source_id is not part of the NormalizedRace model, so this assertion is removed.
    # assert target_race.source_id == "skysports"
