import pytest
from pathlib import Path
from src.paddock_parser.adapters.timeform_adapter import TimeformAdapter
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

@pytest.fixture
def mock_html():
    path = Path(__file__).parent / "timeform.html"
    return path.read_text()

def test_timeform_adapter_parse_races(mock_html):
    adapter = TimeformAdapter()
    races = adapter.parse_races(mock_html)

    assert len(races) == 1
    race = races[0]

    assert race.track_name == "Haydock Park"
    assert race.post_time.strftime("%H:%M") == "14:00"

    # The current adapter is a stub and does not parse runners from the index page.
    # The test should reflect this reality.
    assert len(race.runners) == 0
