# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

from python_service.models import Race, Runner, OddsData

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
    now = datetime.now()
    # This mock response now matches the structure of AggregatedResponse
    mock_response_data = {
        "date": today.isoformat(),
        "races": [
            {
                "id": "test_race_1",
                "venue": "Test Park",
                "race_number": 1,
                "start_time": now.isoformat(),
                "runners": [
                    {
                        "number": 1,
                        "name": "Test Runner 1",
                        "scratched": False,
                        "selection_id": None,
                        "odds": {
                            "TestSource": {
                                "win": "5.0",
                                "source": "TestSource",
                                "last_updated": now.isoformat()
                            }
                        },
                        "jockey": None,
                        "trainer": None
                    }
                ],
                "source": "TestSource",
                "qualification_score": None,
                "race_name": None,
                "distance": None
            }
        ],
        "sources": [
            {
                "name": "TestSource",
                "status": "SUCCESS",
                "races_fetched": 1,
                "error_message": None,
                "fetch_duration": 0.123
            }
        ],
        "metadata": {
            "fetch_time": now.isoformat(),
            "sources_queried": ["TestSource"],
            "sources_successful": 1,
            "total_races": 1
        }
    }
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

    now = datetime.now()
    # The mock response must now provide actual Pydantic models
    mock_engine_response = {
        "races": [
            Race(
                id="test_race_1", venue="Test Park", race_number=1, start_time=now, source="Test",
                runners=[
                    Runner(number=i, name=f"Runner {i}", odds={"TestOdds": OddsData(win=Decimal(2.5 + i), source="Test", last_updated=now)}) for i in range(1, 9)
                ]
            ),
            Race(
                id="test_race_2", venue="Test Park", race_number=2, start_time=now, source="Test",
                runners=[Runner(number=i, name=f"Runner {i}") for i in range(1, 8)]
            ),
            Race(
                id="test_race_3", venue="Test Park", race_number=3, start_time=now, source="Test",
                runners=[
                    Runner(number=i, name=f"Runner {i}", odds={"TestOdds": OddsData(win=Decimal(1.5), source="Test", last_updated=now)}) for i in range(1, 9)
                ]
            )
        ]
    }

    mock_fetch.return_value = mock_engine_response
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get(f"/api/races/qualified/trifecta?race_date={today.isoformat()}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    response_data = response.json()

    assert "criteria" in response_data
    assert "races" in response_data

    qualified_races = response_data['races']
    assert len(qualified_races) == 1
    assert qualified_races[0]["id"] == "test_race_1"

    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'))
