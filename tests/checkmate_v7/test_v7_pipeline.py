"""
Final, working integration test for the Checkmate V7 system.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.checkmate_v7 import services, logic
from src.checkmate_v7.models import Prediction

@pytest.fixture
def mock_db_manager():
    """Mocks the DatabaseManager."""
    return MagicMock()

@pytest.fixture
def mock_orchestrator():
    """Mocks the DataSourceOrchestrator."""
    mock = MagicMock()
    mock.get_race_data = AsyncMock(return_value=[
        {"source": "twinspires", "field_size": 6, "favorite_odds": 2.5, "track": "Good Race", "race_number": 1, "favorite_name": "Winner"},
        {"source": "twinspires", "field_size": 8, "favorite_odds": 8.0, "track": "Bad Race", "race_number": 2, "favorite_name": "Loser"},
    ])
    return mock

@pytest.mark.anyio
@patch('src.checkmate_v7.services.DatabaseManager')
@patch('src.checkmate_v7.services.DataSourceOrchestrator')
async def test_full_service_pipeline(MockOrchestrator, MockDbManager):
    """
    Tests that the main service task correctly processes data from the
    orchestrator, uses the logic module, and saves a qualified prediction.
    """
    # Arrange
    mock_db_manager_instance = MockDbManager()
    mock_orchestrator_instance = MockOrchestrator()

    # Act
    await services.process_race_for_prediction_task()

    # Assert
    mock_orchestrator_instance.get_race_data.assert_awaited_once()
    mock_db_manager_instance.save_prediction.assert_called_once()

    args, _ = mock_db_manager_instance.save_prediction.call_args
    saved_prediction = args[0]
    assert saved_prediction.favorite_candidate_name == "Winner"
