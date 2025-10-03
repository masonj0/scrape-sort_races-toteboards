# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, date

from python_service.api import app
from python_service.engine import OddsEngine

@pytest.fixture
def client():
    """Create a TestClient for the API, which handles the async event loop."""
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status with a timestamp.
    """
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert "timestamp" in json_response
    # Verify the timestamp is a valid ISO 8601 string
    assert isinstance(json_response["timestamp"], str)
    datetime.fromisoformat(json_response["timestamp"])

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_success(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return aggregated data from engine.fetch_all_odds().
    """
    # ARRANGE
    today = date.today()
    mock_response_data = {
        "date": today.isoformat(),
        "races": [{"id": "race1", "venue": "Test Venue"}],
        "sources": [],
        "metadata": {}
    }
    mock_fetch.return_value = mock_response_data

    # ACT
    response = client.get(f"/api/races?race_date={today.isoformat()}")

    # ASSERT
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["date"] == today.isoformat()
    assert response_json["races"] == mock_response_data["races"]
    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'), None)

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_with_source_filter(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should correctly pass the source filter to the engine.
    """
    # ARRANGE
    today = date.today()
    mock_fetch.return_value = {"date": today.isoformat(), "races": [], "sources": [], "metadata": {}}
    source_name = "Betfair"

    # ACT
    response = client.get(f"/api/races?race_date={today.isoformat()}&source={source_name}")

    # ASSERT
    assert response.status_code == 200
    mock_fetch.assert_awaited_once_with(today.strftime('%Y-%m-%d'), source_name)

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_engine_error(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 500 error if the engine raises an exception.
    """
    # ARRANGE
    mock_fetch.side_effect = Exception("A critical engine failure occurred")
    today = date.today()

    # ACT
    response = client.get(f"/api/races?race_date={today.isoformat()}")

    # ASSERT
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    mock_fetch.assert_awaited_once()