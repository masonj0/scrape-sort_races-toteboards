import pytest
from unittest.mock import MagicMock, AsyncMock

from src.checkmate_v7.services import DataSourceOrchestrator
from src.checkmate_v7.adapters.fanduel import FanDuelApiAdapterV7

@pytest.fixture
def mock_session():
    """Provides a mock database session."""
    return MagicMock()

@pytest.mark.anyio
async def test_get_races_returns_status_with_notes(mock_session):
    """
    SPEC: The status dictionary returned by get_races must contain a 'notes' field
    with a human-readable description of the outcome.
    """
    # Arrange
    orchestrator = DataSourceOrchestrator(mock_session)

    # Mock the adapter to simulate it finding no races
    mock_adapter_instance = MagicMock(spec=FanDuelApiAdapterV7)
    mock_adapter_instance.fetch_races = AsyncMock(return_value=[])
    mock_adapter_instance.__class__.__name__ = "FanDuelApiAdapterV7" # Set the name for the status dict

    # Replace the orchestrator's adapter list with our mock
    orchestrator.adapters = [mock_adapter_instance]

    # Act
    races, statuses = await orchestrator.get_races()

    # Assert
    assert len(statuses) == 1
    status = statuses[0]

    # This assertion will fail until the 'notes' field is implemented
    assert "notes" in status
    assert status["notes"] == "No upcoming races found on source."
