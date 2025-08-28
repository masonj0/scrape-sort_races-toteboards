import pathlib
from paddock_parser.adapters.skysports_adapter import SkySportsAdapter

def test_parse_skysports_racecards():
    """
    Tests that the Sky Sports adapter can correctly parse a single meeting card.
    """
    # Path to the HTML fixture
    fixture_path = pathlib.Path(__file__).parent / "fixtures" / "skysports_racecards_sample.html"

    # Read the HTML content
    with open(fixture_path, "r") as f:
        html_content = f.read()

    # Instantiate the adapter and parse the data
    adapter = SkySportsAdapter()
    races = adapter.parse_races(html_content)

    # --- Assertions ---

    # Should find exactly two races in the sample
    assert len(races) == 2

    # --- Race 1 Assertions ---
    race1 = races[0]
    assert race1.track_name == "Wolverhampton (AW)"
    assert race1.race_number == 1
    assert race1.number_of_runners == 9
    assert "Race 1 - BetUK Apprentice Handicap" in race1.race_id

    # --- Race 2 Assertions ---
    race2 = races[1]
    assert race2.track_name == "Wolverhampton (AW)"
    assert race2.race_number == 2
    assert race2.number_of_runners == 10
    assert "Race 2 - BetUK Plus Handicap" in race2.race_id
