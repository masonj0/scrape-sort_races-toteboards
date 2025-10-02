import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Adjust the import path to match the location of your FastAPI app
from python_service.api import app, get_engine
from python_service.engine import EngineManager

# Fixture for the mock engine
@pytest.fixture
def mock_engine():
    """Create a mock EngineManager for testing."""
    engine = MagicMock(spec=EngineManager)
    engine.last_races = {"races": [{"id": "test_race_1"}], "errors": [], "timestamp": 12345}
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
    # ARRANGE
    # TestClient 'client' is already arranged by the fixture

    # ACT
    response = client.get("/health")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_races_returns_mock_data(client, mock_engine):
    """
    SPEC: The /races endpoint should return the data from the EngineManager.
    """
    # ARRANGE
    # The mock_engine is configured by its fixture to return specific data.

    # ACT
    response = client.get("/races")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == mock_engine.last_races
    # Verify that the data returned is what the mock was configured with
    assert response.json()["races"][0]["id"] == "test_race_1"