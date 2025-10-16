import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import date, datetime
from decimal import Decimal

from python_service.adapters.the_racing_api_adapter import TheRacingApiAdapter
from python_service.config import Settings

@pytest.fixture
def mock_config():
    """
    Provides a mock config object for the adapter, ensuring it doesn't
    load from any .env files and provides the necessary API key.
    """
    class TestSettings(Settings):
        class Config:
            env_file = None

    return TestSettings(
        API_KEY="test_api_key",
        THE_RACING_API_KEY="test_racing_api_key"
    )

@pytest.fixture
def mock_config_no_key():
    """Provides a mock config with the API key explicitly set to None."""
    class TestSettings(Settings):
        class Config:
            env_file = None

    return TestSettings(
        API_KEY="test_api_key",
        THE_RACING_API_KEY=None
    )

@pytest.mark.asyncio
@patch('python_service.adapters.the_racing_api_adapter.TheRacingApiAdapter.make_request', new_callable=AsyncMock)
async def test_fetch_races_parses_correctly(mock_make_request, mock_config):
    """
    Tests that TheRacingApiAdapter correctly parses a valid API response.
    """
    # ARRANGE
    adapter = TheRacingApiAdapter(config=mock_config)
    today = date.today().strftime('%Y-%m-%d')
    off_time_str = datetime.utcnow().isoformat() + "Z"


    mock_api_response = {
        "racecards": [
            {
                "race_id": "12345",
                "course": "Newbury",
                "race_no": 3,
                "off_time": off_time_str,
                "race_name": "The Great Race",
                "distance_f": "1m 2f",
                "runners": [
                    {
                        "horse": "Speedy Steed",
                        "number": 1,
                        "jockey": "T. Rider",
                        "trainer": "A. Trainer",
                        "odds": [{"odds_decimal": "5.50"}]
                    },
                    {
                        "horse": "Gallant Gus",
                        "number": 2,
                        "jockey": "J. Jockey",
                        "trainer": "B. Builder",
                        "odds": [{"odds_decimal": "3.25"}]
                    }
                ]
            }
        ]
    }
    mock_response = Mock()
    mock_response.json.return_value = mock_api_response
    mock_make_request.return_value = mock_response

    # ACT
    result = await adapter.fetch_races(today, AsyncMock())

    # ASSERT
    assert result is not None
    assert result['source_info']['status'] == 'SUCCESS'
    assert result['source_info']['races_fetched'] == 1

    races = result['races']
    assert len(races) == 1

    race = races[0]
    assert race.id == 'tra_12345'
    assert race.venue == "Newbury"
    assert race.race_number == 3
    assert race.race_name == "The Great Race"
    assert race.distance == "1m 2f"

    assert len(race.runners) == 2

    runner1 = race.runners[0]
    assert runner1.name == "Speedy Steed"
    assert runner1.number == 1
    assert runner1.jockey == "T. Rider"
    assert runner1.trainer == "A. Trainer"
    assert runner1.odds[adapter.source_name].win == Decimal("5.50")

@pytest.mark.asyncio
@patch('python_service.adapters.the_racing_api_adapter.TheRacingApiAdapter.make_request', new_callable=AsyncMock)
async def test_fetch_races_handles_empty_response(mock_make_request, mock_config):
    """
    Tests that the adapter handles an API response with no racecards.
    """
    # ARRANGE
    adapter = TheRacingApiAdapter(config=mock_config)
    today = date.today().strftime('%Y-%m-%d')
    mock_response = Mock()
    mock_response.json.return_value = {"racecards": []}
    mock_make_request.return_value = mock_response

    # ACT
    result = await adapter.fetch_races(today, AsyncMock())

    # ASSERT
    assert result is not None
    assert result['source_info']['status'] == 'SUCCESS'
    assert result['source_info']['races_fetched'] == 0
    assert result['source_info']['error_message'] == "No racecards found in API response."
    assert len(result['races']) == 0

@pytest.mark.asyncio
async def test_fetch_races_handles_auth_failure(mock_config_no_key):
    """
    Tests that the adapter returns a configuration error if the API key is not set.
    """
    # ARRANGE
    adapter = TheRacingApiAdapter(config=mock_config_no_key)
    today = date.today().strftime('%Y-%m-%d')

    # ACT
    result = await adapter.fetch_races(today, AsyncMock())

    # ASSERT
    assert result is not None
    assert result['source_info']['status'] == 'FAILED'
    assert result['source_info']['races_fetched'] == 0
    assert result['source_info']['error_message'] == "ConfigurationError: THE_RACING_API_KEY not set"
    assert len(result['races']) == 0