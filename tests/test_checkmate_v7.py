import pytest
from fastapi.testclient import TestClient
from src.checkmate_v7.api import app

client = TestClient(app)

from unittest.mock import patch, MagicMock

@patch('redis.Redis.from_url')
def test_health_check_with_mock_redis(mock_from_url):
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_from_url.return_value = mock_redis_instance

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["celery"] == "ok"

def test_get_performance_empty():
    response = client.get("/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bets"] == 0
    assert data["sample_size"] == 0

from unittest.mock import patch, MagicMock
from src.checkmate_v7 import services, logic

@pytest.mark.asyncio
async def test_data_source_orchestrator():
    # Mock the session object
    mock_session = MagicMock()

    orchestrator = services.DataSourceOrchestrator(mock_session)

    # Patch the logic.get_test_data to return a known value
    with patch('src.checkmate_v7.logic.get_test_data') as mock_get_test_data:
        mock_get_test_data.return_value = ["race1", "race2"]

        races = await orchestrator.get_races()

        assert races == ["race1", "race2"]
        mock_get_test_data.assert_called_once()
