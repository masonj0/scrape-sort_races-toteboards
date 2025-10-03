# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from python_service.api import app
from python_service.engine import EngineManager

# Since the engine is now a global instance in api.py, we patch it there.
@pytest.fixture
def client():
    """
    Create a TestClient for the API. The engine is mocked for each test function
    that needs it by using the @patch decorator.
    """
    with TestClient(app) as c:
        yield c

# Test for the /health endpoint
def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# Test for the /races endpoint
@patch('python_service.api.engine', spec=EngineManager)
def test_get_races(mock_engine, client):
    """
    SPEC: The /races endpoint should return data from engine.get_last_races().
    """
    # ARRANGE
    mock_data = {"races": [{"id": "race1"}], "timestamp": 12345.0}
    mock_engine.get_last_races.return_value = mock_data

    # ACT
    response = client.get("/races")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_data
    mock_engine.get_last_races.assert_called_once()

# Test for the /dashboard endpoint
@patch('python_service.api.engine', spec=EngineManager)
def test_get_dashboard(mock_engine, client):
    """
    SPEC: The /dashboard endpoint should return data from engine.get_dashboard_summary().
    """
    # ARRANGE
    mock_data = {
        "last_races_summary": {"races": [], "timestamp": 123},
        "fetcher_failures": [{"adapter": "TestAdapter", "error": "Failed"}]
    }
    mock_engine.get_dashboard_summary.return_value = mock_data

    # ACT
    response = client.get("/dashboard")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_data
    mock_engine.get_dashboard_summary.assert_called_once()

# Test for the /funnel endpoint
@patch('python_service.api.engine', spec=EngineManager)
def test_get_funnel(mock_engine, client):
    """
    SPEC: The /funnel endpoint should return data from engine.get_funnel_statistics().
    """
    # ARRANGE
    mock_data = {
        "races_fetched_by_source": {"Adapter1": 10, "Adapter2": 5},
        "total_races_fetched": 15
    }
    mock_engine.get_funnel_statistics.return_value = mock_data

    # ACT
    response = client.get("/funnel")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_data
    mock_engine.get_funnel_statistics.assert_called_once()