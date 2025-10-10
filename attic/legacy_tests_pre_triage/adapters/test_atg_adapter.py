from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import pytest
from src.paddock_parser.adapters.atg_adapter import AtgAdapter

class TestAtgAdapter:

    @pytest.fixture
    def adapter(self):
        return AtgAdapter()

    @pytest.fixture
    def mock_response_json(self):
        return {
            "data": {
                "game": {
                    "id": "V75_2025-09-10",
                    "status": "RESULTS",
                    "races": [
                        {
                            "id": "1",
                            "name": "Race 1",
                            "startTime": "2025-09-10T12:00:00Z",
                            "horses": [
                                {
                                    "id": "1",
                                    "name": "Horse A",
                                    "money": 1000,
                                    "results": { "place": 1 },
                                    "scratched": False
                                },
                                {
                                    "id": "2",
                                    "name": "Horse B",
                                    "money": 500,
                                    "results": { "place": 2 },
                                    "scratched": False
                                }
                            ]
                        },
                        {
                            "id": "2",
                            "name": "Race 2",
                            "startTime": "2025-09-10T12:30:00Z",
                            "horses": [
                                {
                                    "id": "3",
                                    "name": "Horse C",
                                    "money": 2000,
                                    "results": { "place": 1 },
                                    "scratched": False
                                }
                            ]
                        }
                    ]
                }
            }
        }

    @pytest.mark.anyio
    async def test_fetch_and_parse(self, adapter, mock_response_json):
        # 1. Mock the response object that client.post() will return
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_json
        mock_response.raise_for_status = MagicMock()

        # 2. Mock the client instance that the 'async with' will yield
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        # 3. Patch the AsyncClient class, and configure its __aenter__ to return our mock client instance
        with patch("httpx.AsyncClient") as mock_async_client_class:
            mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

            # 4. Run the fetch method
            races = await adapter.fetch()

            # 5. Assertions
            assert len(races) == 2

            race1 = races[0]
            assert race1.race_id == "1"
            assert race1.race_type == "Race 1"
            assert race1.post_time == datetime(2025, 9, 10, 12, 0, tzinfo=timezone.utc)
            assert race1.number_of_runners == 2
            assert len(race1.runners) == 2

            runner1 = race1.runners[0]
            assert runner1.name == "Horse A"
            assert not runner1.scratched

            race2 = races[1]
            assert race2.race_id == "2"
            assert race2.number_of_runners == 1
