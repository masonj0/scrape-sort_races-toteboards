# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, date

# This is the key fix: We patch the Settings class itself where it is defined.
# This ensures that any part of the application that tries to instantiate
# Settings() will get our mock object instead, avoiding all validation errors.
@pytest.fixture(autouse=True)
def override_settings_for_tests():
    # Create a mock object that has the necessary attributes.
    # We use a MagicMock for simplicity instead of a real Settings object.
    mock_settings = MagicMock()
    mock_settings.API_KEY = "test_api_key"

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
    SPEC: The /health endpoint should be available and return a healthy status.
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