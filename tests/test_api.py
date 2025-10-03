# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, date

from python_service.api import app

@pytest.fixture
def client():
    """Create a TestClient for the API."""
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status.
    """
    # ACT
    response = client.get("/health")
    # ASSERT
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert "timestamp" in json_response

@patch('python_service.api.engine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_default_date(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should call the engine with today's date by default.
    """
    # ARRANGE
    today_str = date.today().strftime('%Y-%m-%d')
    mock_data = {
        "date": today_str,
        "races": [], "sources": [], "metadata": {}
    }
    mock_fetch.return_value = mock_data

    # ACT
    response = client.get("/api/races")

    # ASSERT
    assert response.status_code == 200
    assert response.json()["date"] == today_str
    mock_fetch.assert_called_once_with(today_str, None)

@patch('python_service.api.engine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_specific_date_and_source(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should pass date and source parameters to the engine.
    """
    # ARRANGE
    test_date = "2025-01-15"
    test_source = "Betfair"
    mock_data = {
        "date": test_date,
        "races": [], "sources": [], "metadata": {}
    }
    mock_fetch.return_value = mock_data

    # ACT
    response = client.get(f"/api/races?race_date={test_date}&source={test_source}")

    # ASSERT
    assert response.status_code == 200
    assert response.json()["date"] == test_date
    mock_fetch.assert_called_once_with(test_date, test_source)

@patch('python_service.api.engine.fetch_all_odds', new_callable=AsyncMock)
def test_get_races_engine_exception(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a 500 error if the engine raises an exception.
    """
    # ARRANGE
    mock_fetch.side_effect = Exception("Engine exploded")

    # ACT
    response = client.get("/api/races")

    # ASSERT
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}