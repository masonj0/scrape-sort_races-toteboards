import unittest
from pathlib import Path
from paddock_parser.adapters.equibase_adapter import EquibaseAdapter
from paddock_parser.adapters.base import NormalizedRace, NormalizedRunner

class TestEquibaseAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = EquibaseAdapter()
        # Correctly locate the fixture file relative to the test file's location
        fixture_path = Path(__file__).parent / "fixtures/equibase_sample.html"
        with open(fixture_path, "r", encoding="utf-8") as f:
            self.sample_html = f.read()

    def test_parse_racecard(self):
        """
        Tests the offline parsing of the Equibase racecard.
        """
        # We call the public parse_races method, not the private _parse_racecard
        races = self.adapter.parse_races(self.sample_html)

        self.assertIsNotNone(races)
        self.assertEqual(len(races), 1)

        race = races[0]
        self.assertEqual(race.track_name, "Saratoga")
        self.assertEqual(race.race_number, 1)
        self.assertEqual(race.number_of_runners, 7) # 8 total, 1 scratched
        self.assertEqual(len(race.runners), 8)

        # Deep check on a specific runner
        target_runner = next((r for r in race.runners if r.name == "Dathoss"), None)
        self.assertIsNotNone(target_runner)
        self.assertEqual(target_runner.jockey, "Irad Ortiz, Jr.")
        self.assertEqual(target_runner.trainer, "Michael J. Maker")
        self.assertFalse(target_runner.scratched)
        self.assertAlmostEqual(target_runner.odds, 2.5) # 5/2

        # Check the scratched runner
        scratched_runner = next((r for r in race.runners if r.scratched), None)
        self.assertIsNotNone(scratched_runner)
        self.assertEqual(scratched_runner.name, "Nobel")

if __name__ == '__main__':
    unittest.main()
