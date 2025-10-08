# tests/test_api.py

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

from python_service.models import Race, Runner, OddsData

# The 'client' fixture is automatically available from tests/conftest.py

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_success(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a V3 AggregatedResponse with a valid API key.
    """
    # ARRANGE
    today = date.today()
    now = datetime.now()
    mock_response_data = {
        "date": today.isoformat(),
        "races": [],
        "sources": []
    }
    mock_fetch.return_value = mock_response_data
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get(f"/api/races?race_date={today.isoformat()}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    assert response.json()["date"] == today.isoformat()
    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'), None)

@patch('python_service.engine.OddsEngine.get_all_adapter_statuses')
def test_get_all_adapter_statuses_success(mock_get_statuses, client):
    """
    SPEC: The /api/adapters/status endpoint should return status data for all adapters.
    """
    mock_status_data = [
        {'adapter_name': 'BetfairExchange', 'status': 'OK'},
        {'adapter_name': 'BetfairGreyhound', 'status': 'OK'}
    ]
    mock_get_statuses.return_value = mock_status_data
    headers = {"X-API-Key": "test_api_key"}

    response = client.get("/api/adapters/status", headers=headers)

    assert response.status_code == 200
    assert response.json() == mock_status_data
    mock_get_statuses.assert_called_once()

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_invalid_key(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 403 error with an invalid API key.
    """
    headers = {"X-API-Key": "invalid_key"}
    response = client.get("/api/races", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid or missing API Key"}
    mock_fetch.assert_not_called()

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_no_key(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 403 error with no API key.
    """
    response = client.get("/api/races")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
    mock_fetch.assert_not_called()