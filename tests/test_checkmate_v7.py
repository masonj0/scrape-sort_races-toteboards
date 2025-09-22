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

@patch('src.checkmate_v7.api.get_db_session')
def test_get_performance_empty(mock_get_db):
    # Mock the session to return an empty list for the query
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.all.return_value = []
    mock_get_db.return_value = mock_session

    response = client.get("/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["totalBets"] == 0
    assert data["sampleSize"] == 0
    mock_get_db.assert_called_once()

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
        'src.checkmate_v7.services.FanDuelApiAdapterV7.fetch_races',
        new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = [mock_race]

        # Execute
        races, statuses = await orchestrator.get_races()

        # Assert
        assert len(races) == 1
        assert races[0].race_id == "test_race_1"
        assert isinstance(statuses, list)
        mock_fetch.assert_awaited_once()

@patch('src.checkmate_v7.api.services.DataSourceOrchestrator')
def test_get_all_races_endpoint(MockOrchestrator):
    """
    Tests the /api/v1/races/all endpoint, mocking the data source.
    """
    # --- Mock Setup ---
    mock_orchestrator_instance = AsyncMock()

    # Configure the mock to return a list of simple Race objects
    from src.checkmate_v7.models import Race, Runner
    mock_orchestrator_instance.get_races.return_value = ([
        Race(
            race_id="R1",
            track_name="Test Track",
            race_number=1,
            race_type="Stakes",
            runners=[
                Runner(name="Fav", odds=2.0),
                Runner(name="SecondFav", odds=4.0),
                Runner(name="Third", odds=10.0),
                Runner(name="Fourth", odds=12.0),
                Runner(name="Fifth", odds=15.0),
            ]
        )
    ], [])
    MockOrchestrator.return_value = mock_orchestrator_instance

    # --- Run ---
    response = client.get("/api/v1/races/all")

    # --- Assertions ---
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    race_data = data[0]
    # Check for enrichment fields
    assert "checkmateScore" in race_data
    assert "qualified" in race_data
    assert "trifectaFactors" in race_data

    # Verify the analysis was run correctly for our test case
    # This race should qualify and have a score of 100
    assert race_data["qualified"] is True
    assert race_data["checkmateScore"] == 100
    assert race_data["trifectaFactors"]["fieldSize"]["ok"] is True
