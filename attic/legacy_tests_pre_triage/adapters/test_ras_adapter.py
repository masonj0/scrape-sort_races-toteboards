import unittest
from pathlib import Path
from src.paddock_parser.adapters.ras_adapter import RasAdapter

class TestRasAdapter(unittest.TestCase):
    def setUp(self):
        """Load the sample JSON data from the fixture file."""
        self.adapter = RasAdapter()
        fixture_path = Path(__file__).parent / "racingandsports_sample.json"
        self.sample_json = fixture_path.read_text()

    def test_parse_races_specification(self):
        """
        This test serves as the specification for the RasAdapter based on
        the provided racingandsports_sample.json.
        """
        races = self.adapter.parse_races(self.sample_json)

        self.assertIsNotNone(races)
        # The sample file contains thoroughbred, harness, and greyhound meetings.
        # T: 20, H: 11, G: 20 => Total 51
        self.assertEqual(len(races), 51)

        # Find a specific harness race to verify parsing
        harness_race = next((r for r in races if r.track_name == "Riverina Paceway"), None)
        self.assertIsNotNone(harness_race)
        self.assertEqual(harness_race.race_number, 1)
        self.assertEqual(harness_race.number_of_runners, 0)

        # Find a specific thoroughbred race
        thoroughbred_race = next((r for r in races if r.track_name == "Canberra"), None)
        self.assertIsNotNone(thoroughbred_race)
        self.assertEqual(thoroughbred_race.race_number, 1)

        # Find a specific greyhound race
        greyhound_race = next((r for r in races if r.track_name == "Healesville"), None)
        self.assertIsNotNone(greyhound_race)
        self.assertEqual(greyhound_race.race_number, 1)
