import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Adjust the import path to match the location of your FastAPI app
from python_service.api import app, get_engine
from python_service.engine import EngineManager

# Mock data to be returned by the mocked engine
MOCK_RACES_DATA = {"races": [{"id": "test_race_1"}], "timestamp": 12345}
MOCK_DASHBOARD_DATA = {"last_races_summary": MOCK_RACES_DATA, "fetcher_failures": [{"adapter": "TestAdapter", "error": "Timeout"}]}
MOCK_FUNNEL_DATA = {"races_fetched_by_source": {"TestAdapter": 1}, "total_races_fetched": 1}

# Fixture for the mock engine
@pytest.fixture
def mock_engine():
    """Create a mock EngineManager for testing."""
    engine = MagicMock(spec=EngineManager)
    engine.get_last_races.return_value = MOCK_RACES_DATA
    engine.get_dashboard_summary.return_value = MOCK_DASHBOARD_DATA
    engine.get_funnel_statistics.return_value = MOCK_FUNNEL_DATA
    return engine

# Fixture for the TestClient with the mocked dependency
@pytest.fixture
def client(mock_engine):
    """Create a TestClient with the engine dependency overridden."""
    app.dependency_overrides[get_engine] = lambda: mock_engine
    with TestClient(app) as c:
        yield c
    # Clean up the override after the test
    app.dependency_overrides = {}

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_races(client, mock_engine):
    """
    SPEC: The /races endpoint should return the data from the engine's get_last_races method.
    """
    response = client.get("/races")
    assert response.status_code == 200
    assert response.json() == MOCK_RACES_DATA
    mock_engine.get_last_races.assert_called_once()

def test_get_dashboard(client, mock_engine):
    """
    SPEC: The /dashboard endpoint should return the data from the engine's get_dashboard_summary method.
    """
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert response.json() == MOCK_DASHBOARD_DATA
    mock_engine.get_dashboard_summary.assert_called_once()

def test_get_funnel(client, mock_engine):
    """
    SPEC: The /funnel endpoint should return the data from the engine's get_funnel_statistics method.
    """
    response = client.get("/funnel")
    assert response.status_code == 200
    assert response.json() == MOCK_FUNNEL_DATA
    mock_engine.get_funnel_statistics.assert_called_once()