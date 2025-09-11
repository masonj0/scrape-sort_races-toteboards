import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, AsyncMock

from src.paddock_parser.adapters.pointsbet_adapter import PointsBetAdapter
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

@pytest.fixture
def mock_pointsbet_json():
    """Loads the mock PointsBet API response."""
    fixture_path = Path(__file__).parent / "mock_data" / "pointsbet_sample.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)

def test_pointsbet_adapter_parse_method(mock_pointsbet_json):
    """
    Tests that the PointsBetAdapter's parse method correctly processes
    a raw JSON response into a list of NormalizedRace objects.
    This test acts as the specification for the parsing logic.
    """
    # 1. Setup
    adapter = PointsBetAdapter()
    events_data = mock_pointsbet_json['events']

    # 2. Execution
    parsed_races = adapter.parse(events_data)

    # 3. Assertions
    assert isinstance(parsed_races, list)
    # The mock data has 4 events, but only 2 are valid races with runners.
    assert len(parsed_races) == 2

    # --- Detailed assertions for the first race ---
    first_race = parsed_races[0]
    assert isinstance(first_race, NormalizedRace)
    assert first_race.race_id == "PB-12345"
    assert first_race.track_name == "Flemington"
    assert first_race.race_number == 1
    assert first_race.post_time == datetime.fromisoformat("2025-09-12T13:00:00+00:00")
    assert first_race.number_of_runners == 3
    assert len(first_race.runners) == 3

    # --- Detailed assertions for the first runner of the first race ---
    first_runner = first_race.runners[0]
    assert isinstance(first_runner, NormalizedRunner)
    assert first_runner.name == "Speedy Steed"
    assert first_runner.program_number == 1
    assert first_runner.odds == 4.50

    # --- Check another runner to be sure ---
    third_runner = first_race.runners[2]
    assert third_runner.name == "Wired Winner"
    assert third_runner.program_number == 3
    assert third_runner.odds == 3.20

    # --- Detailed assertions for the second race ---
    second_race = parsed_races[1]
    assert second_race.track_name == "Flemington"
    assert second_race.race_number == 2
    assert len(second_race.runners) == 2

@pytest.mark.anyio
@patch('src.paddock_parser.adapters.pointsbet_adapter.get_page_content', new_callable=AsyncMock)
async def test_pointsbet_adapter_fetch_method(mock_get_page_content, mock_pointsbet_json):
    """
    Tests that the PointsBetAdapter's fetch method correctly calls the fetcher,
    parses the content, and returns a list of NormalizedRace objects.
    """
    # 1. Setup
    mock_get_page_content.return_value = mock_pointsbet_json
    adapter = PointsBetAdapter()

    # 2. Execution
    fetched_races = await adapter.fetch()

    # 3. Assertions
    mock_get_page_content.assert_called_once_with(
        "https://api.au.pointsbet.com/api/v2/racing/races/today",
        response_type='json'
    )

    assert isinstance(fetched_races, list)
    assert len(fetched_races) == 2
    assert fetched_races[0].track_name == "Flemington"
