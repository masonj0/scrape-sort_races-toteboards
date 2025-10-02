import pytest
from unittest.mock import MagicMock

from src.checkmate_v7.services import DataSourceOrchestrator
from src.checkmate_v7.adapters.AndWereOff import FanDuelApiAdapter as FanDuelApiAdapterV7
from src.checkmate_v7.models import Race

@pytest.fixture
def mock_session():
    """Provides a mock database session."""
    return MagicMock()

@pytest.mark.parametrize(
    "adapter_return_value, adapter_side_effect, expected_note, expected_status",
    [
        ([Race(race_id="r1", track_name="TrackA", runners=[])], None, "Successfully parsed 1 races.", "OK"),
        ([], None, "No upcoming races found on source.", "OK"),
        (None, ValueError("Test API Error"), "API Error: Test API Error", "ERROR"),
    ],
    ids=["success", "no_races", "error"]
)
def test_get_races_returns_status_with_notes(
    mock_session, adapter_return_value, adapter_side_effect, expected_note, expected_status
):
    """
    SPEC: The status dictionary returned by get_races must contain a 'notes' field
    with a human-readable description of the outcome for all scenarios.
    """
    # Arrange
    orchestrator = DataSourceOrchestrator(mock_session)

    mock_adapter_instance = MagicMock(spec=FanDuelApiAdapterV7)
    mock_adapter_instance.fetch_races = MagicMock(
        return_value=adapter_return_value,
        side_effect=adapter_side_effect
    )
    mock_adapter_instance.__class__.__name__ = "MockAdapter"

    # The orchestrator should break on the first success, so for the empty and error
    # cases, we need a successful adapter to follow it.
    mock_successful_adapter = MagicMock(spec=FanDuelApiAdapterV7)
    mock_successful_adapter.fetch_races = MagicMock(return_value=[Race(race_id="r2", track_name="TrackB", runners=[])])
    mock_successful_adapter.__class__.__name__ = "SuccessAdapter"

    if expected_status == "OK" and not adapter_return_value:
        orchestrator.adapters = [mock_adapter_instance, mock_successful_adapter]
    elif expected_status == "ERROR":
        orchestrator.adapters = [mock_adapter_instance, mock_successful_adapter]
    else:
        orchestrator.adapters = [mock_adapter_instance]


    # Act
    _, statuses = orchestrator.get_races()

    # Assert
    assert len(statuses) >= 1
    status = statuses[0]

    assert "notes" in status
    assert status["notes"] == expected_note
    assert status["status"] == expected_status
    if expected_status == "ERROR":
        assert status["error_message"] == "Test API Error"
