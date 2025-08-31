import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from paddock_parser.pipeline import run_pipeline
from paddock_parser.base import NormalizedRace, BaseAdapter, BaseAdapterV3

@pytest.mark.anyio
class TestPipeline:

    @patch('paddock_parser.pipeline.load_adapters')
    async def test_pipeline_resilience(self, mock_load_adapters):
        """
        Tests that the pipeline can gracefully handle an adapter that fails.
        """
        # --- Mocks ---
        mock_sky_instance = AsyncMock(spec=BaseAdapterV3)
        mock_sky_instance.SOURCE_ID = "skysports"
        mock_sky_instance.fetch.side_effect = Exception("API request failed")

        mock_fanduel_instance = MagicMock(spec=BaseAdapter)
        mock_fanduel_instance.SOURCE_ID = "fanduel"
        mock_fanduel_instance.fetch_data.return_value = {"schedule": "{}", "detail": "{}"}
        mock_fanduel_instance.parse_data.return_value = [
            NormalizedRace(race_id="fd-1", track_name="FanDuel Track", race_number=1, number_of_runners=5, post_time=None)
        ]

        MockSkyClass = MagicMock(return_value=mock_sky_instance)
        MockFanDuelClass = MagicMock(return_value=mock_fanduel_instance)
        mock_load_adapters.return_value = [MockSkyClass, MockFanDuelClass]

        # --- Run ---
        await run_pipeline(min_runners=1, specific_source=None)

        # --- Assertions ---
        mock_sky_instance.fetch.assert_awaited_once()
        mock_fanduel_instance.fetch_data.assert_called_once()

    @patch('paddock_parser.pipeline.load_adapters')
    async def test_pipeline_end_to_end(self, mock_load_adapters):
        """
        Tests the full end-to-end flow of the pipeline with successful adapters.
        """
        # --- Mocks ---
        mock_sky_instance = AsyncMock(spec=BaseAdapterV3)
        mock_sky_instance.SOURCE_ID = "skysports"
        mock_sky_instance.fetch.return_value = [
            NormalizedRace(race_id="sky-1", track_name="Sky Track", race_number=1, number_of_runners=8, post_time=None)
        ]

        mock_fanduel_instance = MagicMock(spec=BaseAdapter)
        mock_fanduel_instance.SOURCE_ID = "fanduel"
        mock_fanduel_instance.fetch_data.return_value = {"schedule": "{}", "detail": "{}"}
        mock_fanduel_instance.parse_data.return_value = [
            NormalizedRace(race_id="fd-1", track_name="FanDuel Track", race_number=1, number_of_runners=5, post_time=None)
        ]

        MockSkyClass = MagicMock(return_value=mock_sky_instance)
        MockFanDuelClass = MagicMock(return_value=mock_fanduel_instance)
        mock_load_adapters.return_value = [MockSkyClass, MockFanDuelClass]

        # --- Run ---
        await run_pipeline(min_runners=1, specific_source=None)

        # --- Assertions ---
        mock_sky_instance.fetch.assert_awaited_once()
        mock_fanduel_instance.fetch_data.assert_called_once()
        mock_fanduel_instance.parse_data.assert_called_once()
