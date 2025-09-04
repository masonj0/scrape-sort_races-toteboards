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

    expected_runners = [
        NormalizedRunner(name="NIGHT TARA (IRE)", odds=1.25, program_number=1),
        NormalizedRunner(name="OPERA WAVE", odds=4.0, program_number=2),
        NormalizedRunner(name="MYSTICAL MARIA", odds=5.5, program_number=3),
    ]

    assert len(race.runners) == len(expected_runners)

    for i, runner in enumerate(race.runners):
        assert runner.name == expected_runners[i].name
        assert runner.odds == expected_runners[i].odds
