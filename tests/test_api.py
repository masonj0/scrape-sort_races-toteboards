# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, date

# DO NOT import the `app` object at the top level.
# This is the key to preventing the startup validation from running before our patch is in place.
from python_service.config import Settings

# This fixture is the core of the solution. It runs automatically for every test.
# It patches the Settings class within the config module itself. This ensures that
# any code that tries to instantiate Settings() will get our mock object instead,
# completely bypassing the real __init__ and its validation.
@pytest.fixture(autouse=True)
def override_settings_for_tests():
    # Create a test-specific Settings class to prevent loading .env files
    class TestSettings(Settings):
        class Config:
            env_file = None

    mock_settings = TestSettings(
        BETFAIR_APP_KEY="test_key",
        BETFAIR_USERNAME="test_user",
        BETFAIR_PASSWORD="test_password",
        API_KEY="test_api_key",
        TVG_API_KEY="test_tvg_key",
        RACING_AND_SPORTS_TOKEN="test_ras_token",
        POINTSBET_API_KEY="test_pb_key"
    )
    # The patch must target the location where the object is *used*.
    with patch('python_service.config.Settings', return_value=mock_settings):
        yield

@pytest.fixture
def client():
    """
    Create a TestClient for the API. The app is imported *inside* the fixture
    to ensure that the patch from `override_settings_for_tests` is active
    before the app and its lifespan manager are initialized.
    """
    from python_service.api import app
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status with a timestamp.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# The engine is created in the lifespan, so we patch its methods directly
@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_success(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return data with a valid API key.
    """
    # ARRANGE
    today = date.today()
    mock_response_data = {"races": [{"id": "race1"}]}
    mock_fetch.return_value = mock_response_data
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get(f"/api/races?race_date={today.isoformat()}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_response_data
    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'), None)

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_invalid_key(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 403 error with an invalid API key.
    """
    # ARRANGE
    headers = {"X-API-Key": "invalid_key"}

    # ACT
    response = client.get("/api/races", headers=headers)

    # ASSERT
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid or missing API Key"}
    mock_fetch.assert_not_called()

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_no_key(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 403 error with no API key.
    """
    # ARRANGE & ACT
    response = client.get("/api/races")

    # ASSERT
    # The default error from APIKeyHeader(auto_error=True) is "Not authenticated"
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
    mock_fetch.assert_not_called()

@patch('python_service.engine.OddsEngine.get_all_adapter_statuses')
def test_get_all_adapter_statuses_success(mock_get_statuses, client):
    """
    SPEC: The /api/adapters/status endpoint should return status data with a valid API key.
    """
    # ARRANGE
    mock_status_data = [{"adapter_name": "Betfair", "status": "OK"}]
    mock_get_statuses.return_value = mock_status_data
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get("/api/adapters/status", headers=headers)

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_status_data
    mock_get_statuses.assert_called_once()


@patch('python_service.engine.OddsEngine.get_all_adapter_statuses')
def test_get_all_adapter_statuses_invalid_key(mock_get_statuses, client):
    """
    SPEC: The /api/adapters/status endpoint should return a 403 error with an invalid API key.
    """
    # ARRANGE
    headers = {"X-API-Key": "invalid_key"}

    # ACT
    response = client.get("/api/adapters/status", headers=headers)

    # ASSERT
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid or missing API Key"}
    mock_get_statuses.assert_not_called()


@patch('python_service.engine.OddsEngine.get_all_adapter_statuses')
def test_get_all_adapter_statuses_no_key(mock_get_statuses, client):
    """
    SPEC: The /api/adapters/status endpoint should return a 403 error with no API key.
    """
    # ARRANGE & ACT
    response = client.get("/api/adapters/status")

    # ASSERT
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
    mock_get_statuses.assert_not_called()
