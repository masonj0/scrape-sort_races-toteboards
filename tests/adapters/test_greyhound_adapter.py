import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import date, datetime
from python_service.adapters.greyhound_adapter import GreyhoundAdapter
from python_service.config import Settings

@pytest.fixture
def mock_config():
    """
    Provides a mock config object for the adapter, ensuring it doesn't
    load from any .env files, which prevents test pollution.
    """
    class TestSettings(Settings):
        class Config:
            env_file = None

    return TestSettings(
        BETFAIR_APP_KEY="test_key",
        BETFAIR_USERNAME="test_user",
        BETFAIR_PASSWORD="test_password",
        API_KEY="test_api_key",
        GREYHOUND_API_URL="https://api.example.com"
    )

@pytest.mark.asyncio
@patch('python_service.adapters.greyhound_adapter.GreyhoundAdapter.make_request', new_callable=AsyncMock)
async def test_fetch_races_parses_correctly(mock_make_request, mock_config):
    """
    Tests that the GreyhoundAdapter correctly parses a valid API response.
    """
    # ARRANGE
    adapter = GreyhoundAdapter(config=mock_config)
    today = date.today().strftime('%Y-%m-%d')

    mock_api_response = {
        "cards": [
            {
                "track_name": "Test Track",
                "races": [
                    {
                        "race_id": "test_race_123",
                        "race_number": 1,
                        "start_time": int(datetime.now().timestamp()),
                        "runners": [
                            {
                                "dog_name": "Rapid Rover",
                                "trap_number": 1,
                                "odds": {"win": "2.5"}
                            },
                            {
                                "dog_name": "Swift Sprint",
                                "trap_number": 2,
                                "scratched": True
                            },
                            {
                                "dog_name": "Lazy Larry",
                                "trap_number": 3,
                                "odds": {"win": "10.0"}
                            }
                        ]
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
    assert race.id == 'greyhound_test_race_123'
    assert race.venue == 'Test Track'
    assert len(race.runners) == 2 # One was scratched

    runner1 = race.runners[0]
    assert runner1.name == 'Rapid Rover'
    assert runner1.number == 1
    assert runner1.odds['Greyhound Racing'].win == 2.5

@pytest.mark.asyncio
@patch('python_service.adapters.greyhound_adapter.GreyhoundAdapter.make_request', new_callable=AsyncMock)
async def test_fetch_races_handles_empty_response(mock_make_request, mock_config):
    """
    Tests that the GreyhoundAdapter handles an empty or invalid API response gracefully.
    """
    # ARRANGE
    adapter = GreyhoundAdapter(config=mock_config)
    today = date.today().strftime('%Y-%m-%d')
    mock_response = Mock()
    mock_response.json.return_value = {"cards": []}
    mock_make_request.return_value = mock_response

    # ACT
    result = await adapter.fetch_races(today, AsyncMock())

    # ASSERT
    assert result is not None
    assert result['source_info']['status'] == 'SUCCESS'
    assert result['source_info']['races_fetched'] == 0
    assert result['source_info']['error_message'] == "No race cards found for date."
    assert len(result['races']) == 0