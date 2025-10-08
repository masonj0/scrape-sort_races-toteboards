import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from python_service.config import Settings

@pytest.fixture(autouse=True)
def override_settings_for_tests():
    """
    Patches the Settings class for all tests to prevent loading .env files
    and to provide a consistent, mock configuration. This runs automatically.
    """
    class TestSettings(Settings):
        class Config:
            env_file = None

    mock_settings = TestSettings(
        BETFAIR_APP_KEY="test_key",
        BETFAIR_USERNAME="test_user",
        BETFAIR_PASSWORD="test_password",
        API_KEY="test_api_key",
        TVG_API_KEY="test_tvg_key",
        RACING_AND_SPORTS_TOKEN="test_ras_token"
    )
    with patch('python_service.config.Settings', return_value=mock_settings):
        yield

@pytest.fixture
def client():
    """
    Creates a TestClient for the API. The app is imported *inside* this
    fixture to ensure the settings patch is active before initialization.
    """
    from python_service.api import app
    with TestClient(app) as c:
        yield c