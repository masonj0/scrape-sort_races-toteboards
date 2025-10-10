import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from paddock_parser.adapters.racingpost_adapter import RacingPostAdapter

class TestRacingPostAdapter(unittest.TestCase):
    def setUp(self):
        """
        Load the sample HTML data from the fixture file.
        """
        self.adapter = RacingPostAdapter()
        fixture_path = Path(__file__).parent / "mock_data" / "racingpost_sample.html"
        self.sample_html = fixture_path.read_text(encoding="utf-8")

    def test_parse_racecard_specification(self):
        """
        This test serves as the specification for the RacingPostAdapter based on
        the provided racingpost_sample.html.
        """
        races = self.adapter.parse_races(self.sample_html)

        # There are multiple races on the page, but the sample HTML only contains details for the first one.
        self.assertIsNotNone(races)
        self.assertEqual(len(races), 1)

        first_race = races[0]
        self.assertEqual(first_race.track_name, "Bellewstown")

        # The post time in the JSON is "2025-08-26T16:25:00+01:00"
        expected_post_time = datetime(2025, 8, 26, 16, 25, tzinfo=timezone(timedelta(hours=1)))
        self.assertEqual(first_race.post_time, expected_post_time)

        self.assertEqual(first_race.race_type, "Irish Stallion Farms EBF Median Auction Maiden")

        # The sample HTML file seems to only contain the data for the first race's runners,
        # even though the JSON lists competitors for the whole day.
        # There are 15 runners listed for the first race, and 2 non-runners.
        self.assertEqual(first_race.number_of_runners, 15)
        self.assertEqual(len(first_race.runners), 15)

        self.assertEqual(first_race.race_id, "902106")

        # Test a specific runner (Pete's Dream, runner #5)
        petes_dream = next((r for r in first_race.runners if r.program_number == 5), None)
        self.assertIsNotNone(petes_dream)
        self.assertEqual(petes_dream.name, "Pete's Dream")
        self.assertEqual(petes_dream.jockey, "Andrew Slattery")
        self.assertEqual(petes_dream.trainer, "Andrew Slattery")
        self.assertEqual(petes_dream.odds, 11.0)

        # Test another runner to be sure (Arrumba, runner #1)
        arrumba = next((r for r in first_race.runners if r.program_number == 1), None)
        self.assertIsNotNone(arrumba)
        self.assertEqual(arrumba.name, "Arrumba")
        self.assertEqual(arrumba.jockey, "Sam Coen")
        self.assertEqual(arrumba.trainer, "Mrs Denise Foster")
        self.assertEqual(arrumba.odds, 23.0)
