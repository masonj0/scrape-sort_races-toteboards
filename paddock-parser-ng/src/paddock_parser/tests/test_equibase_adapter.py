import unittest
from pathlib import Path
from paddock_parser.adapters.equibase_adapter import EquibaseAdapter
from paddock_parser.adapters.base import NormalizedRace, NormalizedRunner

class TestEquibaseAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = EquibaseAdapter()
        # Use a direct path from the project root to avoid ambiguity
        fixture_path = "src/paddock_parser/tests/fixtures/equibase_sample.html"
        with open(fixture_path, "r", encoding="utf-8") as f:
            self.sample_html = f.read()

    def test_parse_racecard(self):
        """
        Tests the offline parsing of the Equibase racecard.
        """
        races = self.adapter.parse_races(self.sample_html)

        self.assertIsNotNone(races)
        self.assertEqual(len(races), 10)

        # Test the first race
        first_race = races[0]
        self.assertEqual(first_race.track_name, "Saratoga")
        self.assertEqual(first_race.race_number, 1)
        self.assertEqual(first_race.race_type, "Maiden Special Weight")
        self.assertEqual(first_race.number_of_runners, 9)
        self.assertEqual(len(first_race.runners), 0)

        # Test the last race
        last_race = races[9]
        self.assertEqual(last_race.track_name, "Saratoga")
        self.assertEqual(last_race.race_number, 10)
        self.assertEqual(last_race.race_type, "Claiming")
        self.assertEqual(last_race.number_of_runners, 14)
        self.assertEqual(len(last_race.runners), 0)

if __name__ == '__main__':
    unittest.main()
