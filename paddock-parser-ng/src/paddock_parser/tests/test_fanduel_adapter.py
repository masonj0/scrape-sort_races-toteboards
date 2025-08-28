import json
import pathlib
from datetime import datetime

from paddock_parser.adapters.fanduel_graphql_adapter import parse_from_json
from paddock_parser.adapters.models import NormalizedRace, NormalizedRunner

def test_parse_from_json():
    """
    Tests that the FanDuel GraphQL JSON parsing and normalization logic is correct.
    """
    # Get the path to the fixtures directory
    fixtures_dir = pathlib.Path(__file__).parent / "fixtures"

    # Load the schedule and detail data from the fixture files
    with open(fixtures_dir / "fanduel_schedule_sample.json", "r") as f:
        schedule_data = f.read()

    with open(fixtures_dir / "fanduel_race_detail_sample.json", "r") as f:
        detail_data = f.read()

    # Call the parsing function
    result = parse_from_json(schedule_data, detail_data)

    # --- Assertions ---

    # Assert that we get a list with one race
    assert isinstance(result, list)
    assert len(result) == 1

    race = result[0]
    assert isinstance(race, NormalizedRace)

    # Assertions for the NormalizedRace object
    assert race.race_id == "HOO-6"
    assert race.track_name == "AU - Belmont Park"
    assert race.race_number == 1
    assert race.post_time == datetime.fromisoformat("2025-08-27T05:39:01+00:00")
    assert race.race_type == "T"
    assert race.minutes_to_post == 428

    # Assertions for the runners
    assert isinstance(race.runners, list)
    assert len(race.runners) == 2

    # First runner
    runner1 = race.runners[0]
    assert isinstance(runner1, NormalizedRunner)
    assert runner1.name == "Pay Me No Mind"
    assert runner1.program_number == 1
    assert not runner1.scratched
    assert runner1.jockey == "Finn, J D"
    assert runner1.trainer == "Finn, Jared"
    assert runner1.odds == "12-1"

    # Second runner
    runner2 = race.runners[1]
    assert isinstance(runner2, NormalizedRunner)
    assert runner2.name == "Don't Tell Ur Mom"
    assert runner2.program_number == 2
    assert not runner2.scratched
    assert runner2.jockey == "Bender, Atlee"
    assert runner2.trainer == "Putnam, Joe"
    assert runner2.odds == "5-1"
