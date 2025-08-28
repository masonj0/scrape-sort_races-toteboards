import unittest
from unittest.mock import patch, MagicMock

import unittest
from unittest.mock import patch, MagicMock

# Corrected import paths
from paddock_parser.pipeline import run_analysis_pipeline
from paddock_parser.adapters.base import NormalizedRace, BaseAdapter, BaseAdapterV3

class TestPipeline(unittest.TestCase):

    @patch('paddock_parser.pipeline.view_text_website')
    @patch('paddock_parser.pipeline.load_adapters')
    def test_pipeline_resilience_to_failing_adapter(self, mock_load_adapters, mock_view_text_website):
        """
        Tests that the pipeline can gracefully handle an adapter that fails during fetch.
        """
        # --- Setup Mocks ---

        # Create a mock instance for the SkySportsAdapter
        mock_sky_instance = MagicMock(spec=BaseAdapterV3)
        mock_sky_instance.SOURCE_ID = "skysports"
        mock_sky_instance.url = "http://sky.com"
        mock_sky_instance.parse_races.return_value = [
            NormalizedRace(race_id="test-1", track_name="Test Track", race_number=1, number_of_runners=5)
        ]

        # Create a mock instance for the FanDuel adapter
        mock_fanduel_instance = MagicMock(spec=BaseAdapter)
        mock_fanduel_instance.SOURCE_ID = "fanduel"
        mock_fanduel_instance.fetch.side_effect = Exception("API request failed")

        # Create mock *classes* that will be returned by load_adapters
        MockSkyClass = MagicMock(name="MockSkyClass")
        MockFanDuelClass = MagicMock(name="MockFanDuelClass")

        # Configure the mock classes to return our prepared instances when they are instantiated
        MockSkyClass.return_value = mock_sky_instance
        MockFanDuelClass.return_value = mock_fanduel_instance

        # load_adapters returns a list of CLASSES
        mock_load_adapters.return_value = [MockSkyClass, MockFanDuelClass]

        mock_view_text_website.return_value = "<html></html>"

        # --- Run Pipeline ---
        try:
            run_analysis_pipeline()
        except Exception as e:
            self.fail(f"Pipeline crashed with an unexpected exception: {e}")

        # --- Assertions ---
        mock_view_text_website.assert_called_once_with("http://sky.com")
        mock_sky_instance.parse_races.assert_called_once()
        # The fanduel adapter uses the V1 'parse' method, which should not be called.
        mock_fanduel_instance.parse.assert_not_called()

    @patch('paddock_parser.pipeline.view_text_website')
    @patch('paddock_parser.pipeline.load_adapters')
    def test_pipeline_end_to_end_flow(self, mock_load_adapters, mock_view_text_website):
        """
        Tests the full end-to-end flow of the pipeline with a successful adapter.
        """
        # --- Setup Mocks ---

        # Create a mock instance for the SkySportsAdapter
        mock_sky_instance = MagicMock(spec=BaseAdapterV3)
        mock_sky_instance.SOURCE_ID = "skysports"
        mock_sky_instance.url = "http://sky.com"
        mock_sky_instance.parse_races.return_value = [
            NormalizedRace(race_id="test-1", track_name="Test Track", race_number=1, number_of_runners=5),
            NormalizedRace(race_id="test-2", track_name="Test Track", race_number=2, number_of_runners=10),
        ]

        # Create a mock class
        MockSkyClass = MagicMock(name="MockSkyClass")
        # Configure it to return our instance when instantiated
        MockSkyClass.return_value = mock_sky_instance

        # load_adapters returns a list of CLASSES
        mock_load_adapters.return_value = [MockSkyClass]
        mock_view_text_website.return_value = "<html></html>"

        # --- Run Pipeline ---
        run_analysis_pipeline()

        # --- Assertions ---
        mock_load_adapters.assert_called_once()
        mock_view_text_website.assert_called_once_with("http://sky.com")
        mock_sky_instance.parse_races.assert_called_once()

if __name__ == '__main__':
    unittest.main()
