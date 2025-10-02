import unittest
from pathlib import Path

from paddock_parser.adapters.greyhound_recorder import GreyhoundRecorderAdapter


class TestGreyhoundRecorderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = GreyhoundRecorderAdapter()
        fixture_path = Path(__file__).parent / "mock_data" / "greyhound_recorder_sample.html"
        self.html_content = fixture_path.read_text(encoding="utf-8")

    def test_parse_races_from_sample(self):
        self.assertIn("</html>", self.html_content, "Sample HTML file could not be read.")

        races = self.adapter.parse_races(self.html_content)

        # There are 12 races for 2 tracks in the sample file
        self.assertEqual(len(races), 12)

        # Test the first race for correct structure and data
        first_race = races[0]
        self.assertEqual(first_race.race_id, '1035251')
        self.assertEqual(first_race.track_name, 'Crayford')
        self.assertEqual(first_race.race_number, 1)
        self.assertEqual(len(first_race.runners), 6)

        # Test the first runner of the first race
        first_runner = first_race.runners[0]
        self.assertEqual(first_runner.name, 'Deanridge Awesom')
        self.assertEqual(first_runner.program_number, 1)
        self.assertEqual(first_runner.trainer, 'A W Kelly')

        # Test the last race (first race of the second track)
        last_race = races[6]
        self.assertEqual(last_race.race_id, '1035415')
        self.assertEqual(last_race.track_name, 'Monmore')
        self.assertEqual(last_race.race_number, 1)
        self.assertEqual(len(last_race.runners), 6)
        self.assertEqual(last_race.runners[0].name, 'Final Bullet')
