# tests/adapters/test_pointsbet_adapter.py

import pytest
import httpx
import respx
from unittest.mock import MagicMock

from python_service.adapters.pointsbet_adapter import PointsBetAdapter
from python_service.config import Settings

# Mock response from the PointsBet API
mock_api_response = {
    "events": [
        {
            "id": "PB12345",
            "competitionName": "Flemington",
            "eventNumber": 1,
            "startTime": "2025-10-04T04:30:00Z",
            "outcomes": [
                {
                    "name": "Horse A",
                    "isSuspended": False,
                    "prices": [{"priceType": "FixedWin", "price": 5.50}]
                },
                {
                    "name": "Horse B",
                    "isSuspended": False,
                    "prices": [{"priceType": "FixedWin", "price": 2.20}]
                },
                {
                    "name": "Scratched Horse",
                    "isSuspended": True,
                    "prices": [{"priceType": "FixedWin", "price": 10.0}]
                }
            ]
        },
        {
            "id": "PB67890",
            "competitionName": "Randwick",
            "eventNumber": 2,
            "startTime": "2025-10-05T05:00:00Z", # Different date
            "outcomes": [
                {
                    "name": "Horse C",
                    "isSuspended": False,
                    "prices": [{"priceType": "FixedWin", "price": 3.0}]
                }
            ]
        }
    ]
}

@pytest.fixture
def mock_config():
    """Provides a mock config object for tests."""
    return Settings(
        BETFAIR_APP_KEY="test",
        BETFAIR_USERNAME="test",
        BETFAIR_PASSWORD="test",
        API_KEY="test",
        POINTSBET_API_KEY="fake_key",
        _env_file=None
    )

@pytest.fixture
def mock_config_no_key():
    """Provides a mock config with the PointsBet key missing."""
    return Settings(
        BETFAIR_APP_KEY="test",
        BETFAIR_USERNAME="test",
        BETFAIR_PASSWORD="test",
        API_KEY="test",
        POINTSBET_API_KEY=None,
        _env_file=None
    )

@pytest.mark.asyncio
@respx.mock
async def test_fetch_races_success(mock_config):
    """
    SPEC: The adapter should correctly fetch and parse race data from the API.
    It should also correctly filter races to only include those on the requested date.
    """
    # ARRANGE
    # Mock the API endpoint
    respx.get("https://api.au.pointsbet.com/api/v2/racing/futures?sportId=21").mock(
        return_value=httpx.Response(200, json=mock_api_response)
    )

    async with httpx.AsyncClient() as client:
        adapter = PointsBetAdapter(config=mock_config)

        # ACT
        result = await adapter.fetch_races(date="2025-10-04", http_client=client)

    # ASSERT
    races = result['races']
    assert result['source_info']['status'] == 'SUCCESS'
    assert len(races) == 1  # Should filter out the race on the 5th

    race = races[0]
    assert race['id'] == "pb_PB12345"
    assert race['venue'] == "Flemington"
    assert race['race_number'] == 1
    assert len(race['runners']) == 3 # includes scratched horse

    runner = race['runners'][1]
    assert runner['name'] == "Horse B"
    assert runner['scratched'] is False
    assert str(runner['odds']['PointsBet']['win']) == '2.2'

@pytest.mark.asyncio
async def test_fetch_races_no_api_key(mock_config_no_key):
    """
    SPEC: If the API key is not configured, the adapter should return an empty result with a configuration error.
    """
    # ARRANGE
    async with httpx.AsyncClient() as client:
        adapter = PointsBetAdapter(config=mock_config_no_key)

        # ACT
        result = await adapter.fetch_races(date="2025-10-04", http_client=client)

    # ASSERT
    assert result['source_info']['status'] == 'FAILED'
    assert result['source_info']['error_message'] == "ConfigurationError: Token not set"
    assert len(result['races']) == 0

@pytest.mark.asyncio
@respx.mock
async def test_fetch_races_api_error(mock_config):
    """
    SPEC: If the API returns an error, the adapter should raise an exception.
    """
    # ARRANGE
    respx.get("https://api.au.pointsbet.com/api/v2/racing/futures?sportId=21").mock(
        return_value=httpx.Response(500)
    )

    async with httpx.AsyncClient() as client:
        adapter = PointsBetAdapter(config=mock_config)

        # ACT & ASSERT
        with pytest.raises(httpx.HTTPStatusError):
            await adapter.fetch_races(date="2025-10-04", http_client=client)