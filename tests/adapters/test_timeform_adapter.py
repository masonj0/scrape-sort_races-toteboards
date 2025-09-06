import pytest
from pathlib import Path
from paddock_parser.adapters.timeform_adapter import TimeformAdapter
from paddock_parser.base import NormalizedRace

@pytest.fixture
def mock_html():
    path = Path(__file__).parent / "timeform.html"
    return path.read_text()

def test_timeform_adapter_parse_races(mock_html):
    adapter = TimeformAdapter()
    races = adapter.parse_races(mock_html)

    assert len(races) == 35

    # Test the first race specifically
    race = races[0]
    assert race.track_name == "Haydock Park"
    assert race.post_time.strftime("%H:%M") == "14:00"
    assert race.number_of_runners == 0
    assert len(race.runners) == 0

    # Test the last race to be sure
    last_race = races[-1]
    assert last_race.track_name == "Laytown (IRE)"
    assert last_race.post_time.strftime("%H:%M") == "19:10"
