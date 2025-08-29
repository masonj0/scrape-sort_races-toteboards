import pytest
from paddock_parser.models.race import RaceStatus
from paddock_parser.parsers.equibase import EquibaseAdapter


@pytest.fixture
def sample_html():
    with open("src/paddock_parser/fixtures/equibase_sample.html", "r") as f:
        return f.read()


def test_parse_races(sample_html):
    adapter = EquibaseAdapter()
    races = adapter.parse_races(sample_html)
    assert len(races) == 10

    # Test the first race
    race = races[0]
    assert race.race_id == "SAR-2025-08-22-1"
    assert race.source_id == "SAR-2025-08-22-1"
    assert race.source_name == "equibase"
    assert race.name == "Maiden Special Weight"
    assert race.status == RaceStatus.OPEN
    assert race.purse == 90000
    assert race.distance == "5 1/2 F"
    assert race.surface == "Turf"
    assert len(race.runners) == 9

    # Test a runner from the first race (placeholder)
    assert race.runners[0].name == "Runner 1"
    assert race.runners[0].source_id == "1"

    # Test the last race
    race = races[9]
    assert race.race_id == "SAR-2025-08-22-10"
    assert race.purse == 50000
    assert race.distance == "5 1/2 F"
    assert race.surface == "Turf"
    assert len(race.runners) == 14
