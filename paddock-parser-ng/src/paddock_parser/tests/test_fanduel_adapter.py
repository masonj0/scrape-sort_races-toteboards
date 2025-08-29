import json
import unittest
from datetime import datetime
from paddock_parser.adapters.fanduel_graphql_adapter import FanDuelGraphQLAdapter
from paddock_parser.adapters.base import NormalizedRace, NormalizedRunner

class TestFanDuelAdapter(unittest.TestCase):

    def test_parse_data_as_specification(self):
        """
        This test serves as the specification for the FanDuel adapter.
        It defines the expected output structure for a given input.
        The adapter should be implemented to make this test pass.
        """
        adapter = FanDuelGraphQLAdapter()

        # --- Input Data (The Specification) ---
        # This is placeholder data. The real data will be provided later.
        # For now, we define the structure we expect to receive.
        mock_schedule_data = {
            "data": {
                "scheduleRaces": [
                    {
                        "id": "SA",
                        "races": [
                            {
                                "id": "SA-5",
                                "tvgRaceId": 12345,
                                "mtp": 10,
                                "number": "5",
                                "postTime": "2025-09-01T15:30:00Z",
                                "isGreyhound": False,
                                "type": {"code": "T"},
                                "track": {"name": "Santa Anita"}
                            }
                        ]
                    }
                ]
            }
        }

        mock_detail_data = {
            "data": {
                "races": [
                    {
                        "id": "SA-5",
                        "tvgRaceId": 12345,
                        "bettingInterests": [
                            {
                                "biNumber": 1,
                                "runners": [{"scratched": False, "horseName": "Speedy Gonzales", "jockey": "Buggs, B", "trainer": "Jones, W. E."}],
                                "currentOdds": {"numerator": 8, "denominator": 1}
                            },
                            {
                                "biNumber": 2,
                                "runners": [{"scratched": False, "horseName": "Road Runner", "jockey": "Coyote, W", "trainer": "Acme, Corp"}],
                                "currentOdds": {"numerator": 3, "denominator": 1}
                            },
                            {
                                "biNumber": 3,
                                "runners": [{"scratched": True, "horseName": "Slowpoke Rodriguez", "jockey": "Mouse, D", "trainer": "Hanna, B."}],
                                "currentOdds": {}
                            }
                        ]
                    }
                ]
            }
        }

        # The raw_data passed to parse_data will be a dict of JSON strings
        raw_data = {
            "schedule": json.dumps(mock_schedule_data),
            "detail": json.dumps(mock_detail_data)
        }

        # --- Run the parsing logic ---
        result = adapter.parse_data(raw_data)

        # --- Assertions (The Specification) ---
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        race = result[0]
        self.assertIsInstance(race, NormalizedRace)

        # Assertions for the NormalizedRace object
        self.assertEqual(race.race_id, "SA-5")
        self.assertEqual(race.track_name, "Santa Anita")
        self.assertEqual(race.race_number, 5)
        self.assertEqual(race.post_time, datetime.fromisoformat("2025-09-01T15:30:00+00:00"))
        self.assertEqual(race.race_type, "T")
        self.assertEqual(race.minutes_to_post, 10)
        self.assertEqual(race.number_of_runners, 2) # Only non-scratched runners

        # Assertions for the runners
        self.assertIsInstance(race.runners, list)
        self.assertEqual(len(race.runners), 2)

        # Runner 1
        runner1 = race.runners[0]
        self.assertIsInstance(runner1, NormalizedRunner)
        self.assertEqual(runner1.name, "Speedy Gonzales")
        self.assertEqual(runner1.program_number, 1)
        self.assertFalse(runner1.scratched)
        self.assertEqual(runner1.jockey, "Buggs, B")
        self.assertEqual(runner1.trainer, "Jones, W. E.")
        self.assertEqual(runner1.odds, "8-1")

        # Runner 2
        runner2 = race.runners[1]
        self.assertIsInstance(runner2, NormalizedRunner)
        self.assertEqual(runner2.name, "Road Runner")
        self.assertEqual(runner2.program_number, 2)
        self.assertFalse(runner2.scratched)
        self.assertEqual(runner2.jockey, "Coyote, W")
        self.assertEqual(runner2.trainer, "Acme, Corp")
        self.assertEqual(runner2.odds, "3-1")

if __name__ == '__main__':
    unittest.main()
