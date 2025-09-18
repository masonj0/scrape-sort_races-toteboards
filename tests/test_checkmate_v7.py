import pytest
from fastapi.testclient import TestClient
from src.checkmate_v7.api import app

client = TestClient(app)

from unittest.mock import patch, MagicMock

@patch('src.checkmate_v7.api.get_db_session')
@patch('redis.Redis.from_url')
def test_health_check_fully_mocked(mock_redis_from_url, mock_get_db):
    """
    Tests the health check endpoint with both Redis and the DB fully mocked.
    """
    # Mock Redis
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_redis_from_url.return_value = mock_redis_instance

    # Mock Database Session
    mock_db_session = MagicMock()
    mock_get_db.return_value = mock_db_session

    # Execute
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["celery"] == "ok"

    mock_get_db.assert_called_once()
    # The application code wraps the SQL in a text() clause, so we need to
    # assert the call was made and then check the string representation.
    mock_db_session.execute.assert_called_once()
    called_arg = mock_db_session.execute.call_args[0][0]
    assert str(called_arg) == "SELECT 1"
    mock_redis_from_url.assert_called_once()

def test_get_performance_empty():
    response = client.get("/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bets"] == 0
    assert data["sample_size"] == 0

from unittest.mock import patch, MagicMock, AsyncMock
from src.checkmate_v7 import services
from src.checkmate_v7.models import Race

@pytest.mark.anyio
async def test_data_source_orchestrator_v7():
    """
    Tests the new V7 DataSourceOrchestrator logic by mocking an adapter.
    """
    mock_session = MagicMock()
    orchestrator = services.DataSourceOrchestrator(mock_session)

    # Prepare mock race data
    mock_race = Race(race_id="test_race_1", track_name="Test Track", race_number=1, runners=[])

    # Patch the fetch_races method of the first real adapter in the list
    with patch(
        'src.checkmate_v7.services.PointsBetAdapterV7.fetch_races',
        new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = [mock_race]

        # Execute
        races = await orchestrator.get_races()

        # Assert
        assert len(races) == 1
        assert races[0].race_id == "test_race_1"
        mock_fetch.assert_awaited_once()
