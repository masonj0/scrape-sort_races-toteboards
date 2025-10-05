# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, date

# Imports are now cleaner as fixtures are in conftest.py

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


@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_qualified_races_success(mock_fetch, client):
    """
    SPEC: The /api/races/qualified endpoint should return a correctly filtered list of races.
    """
    # ARRANGE
    today = date.today()
    now_iso = datetime.now().isoformat()

    mock_engine_response = {
        "races": [
            { # This race should be qualified (8 runners, fav_odds > 2.0)
                "id": "test_race_1", "venue": "Test Park", "race_number": 1, "start_time": now_iso, "source": "Test",
                "runners": [
                    {"number": i, "name": f"Runner {i}", "scratched": False, "odds": {"TestOdds": {"win": 2.5 + i, "source": "TestOdds", "last_updated": now_iso}}} for i in range(1, 9)
                ]
            },
            { # This race should be filtered out (not enough runners)
                "id": "test_race_2", "venue": "Test Park", "race_number": 2, "start_time": now_iso, "source": "Test",
                "runners": [
                    {"number": i, "name": f"Runner {i}", "scratched": False, "odds": {}} for i in range(1, 8)
                ]
            },
            { # This race should be filtered out (favorite odds too low)
                "id": "test_race_3", "venue": "Test Park", "race_number": 3, "start_time": now_iso, "source": "Test",
                "runners": [
                    {"number": i, "name": f"Runner {i}", "scratched": False, "odds": {"TestOdds": {"win": 1.5, "source": "TestOdds", "last_updated": now_iso}}} for i in range(1, 9)
                ]
            }
        ]
    }

    mock_fetch.return_value = mock_engine_response
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get(f"/api/races/qualified/trifecta?race_date={today.isoformat()}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == "test_race_1"
    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'))
