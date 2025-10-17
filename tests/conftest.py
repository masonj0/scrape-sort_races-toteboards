import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from python_service.config import Settings
from cryptography.fernet import Fernet

@pytest.fixture(autouse=True)
def override_settings_for_tests():
    """
    Patches the get_settings function for all tests to prevent loading .env files
    and to provide a consistent, mock configuration. This runs automatically.
    """
    key = b'Jha6z25yPJ_6I5jmwjBkYbPDYXtsRVQq5LFAG0Nm7X0='
    cipher = Fernet(key)

    mock_settings = Settings(
        BETFAIR_APP_KEY=f"encrypted:{cipher.encrypt(b'test_key').decode()}",
        BETFAIR_USERNAME=f"encrypted:{cipher.encrypt(b'test_user').decode()}",
        BETFAIR_PASSWORD=f"encrypted:{cipher.encrypt(b'test_password').decode()}",
        API_KEY="test_api_key"
    )
    with patch('python_service.config.get_settings', return_value=mock_settings):
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