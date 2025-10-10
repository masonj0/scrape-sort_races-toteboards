import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Import the app from the correct module
from src.checkmate_v7.api import app
from src.checkmate_v7.models import Race # For creating mock race objects

client = TestClient(app)

# --- Mocks and Fixtures ---

@pytest.fixture
def mock_races():
    """Provides a sample list of Race objects."""
    return [
        Race(race_id="R1", track_name="Aqueduct", runners=[]),
        Race(race_id="R2", track_name="Santa Anita", runners=[]),
    ]

@pytest.fixture
def mock_statuses():
    """Provides a sample list of adapter status dictionaries, including the new 'notes' field."""
    return [
        {
            "adapter_id": "FanDuelApiAdapterV7",
            "status": "OK", "races_found": 2, "error_message": None, "notes": "Successfully parsed 2 races.",
            "last_run": "2025-09-20T12:00:00Z"
        },
        {
            "adapter_id": "TwinspiresModernAdapter",
            "status": "ERROR", "races_found": 0, "error_message": "Connection timed out", "notes": "API Error: Connection timed out",
            "last_run": "2025-09-20T12:00:05Z"
        }
    ]

# --- Tests ---

def test_get_adapter_status_endpoint_returns_correct_data(mock_statuses):
    """
    SPEC: The /api/v1/adapters/status endpoint should call the orchestrator,
    extract the status list, and return it as JSON with a 200 OK status.
    """
    with patch('src.checkmate_v7.api.services.DataSourceOrchestrator') as MockOrchestrator:
        mock_instance = MockOrchestrator.return_value
        # Mock get_races to return the new tuple format
        mock_instance.get_races = AsyncMock(return_value=([], mock_statuses))

        response = client.get("/api/v1/adapters/status")

        # This will fail until the endpoint is created
        assert response.status_code == 200
        assert response.json() == mock_statuses

def test_get_races_all_endpoint_handles_new_signature(mock_races, mock_statuses):
    """
    SPEC: The /api/v1/races/all endpoint must be updated to handle the new
    tuple return signature from get_races, extracting only the race list.
    """
    with patch('src.checkmate_v7.api.services.DataSourceOrchestrator') as MockOrchestrator:
        mock_instance = MockOrchestrator.return_value
        # Mock get_races to return the new tuple format
        mock_instance.get_races.return_value = (mock_races, mock_statuses)

        response = client.get("/api/v1/races/all")

        # This will fail until the endpoint is updated to unpack the tuple
        assert response.status_code == 200

        # The endpoint should ignore the statuses and return only the races,
        # which then get mapped to the RaceDataSchema.
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["id"] == "R1"
        assert response_data[1]["track"] == "Santa Anita"

def test_post_refresh_action_endpoint():
    """
    Tests the new POST /api/v1/actions/refresh endpoint.
    It should simply return a 200 OK with the specified acknowledgement message.
    """
    # Act
    response = client.post("/api/v1/actions/refresh")

    # Assert
    assert response.status_code == 200
    expected_response = {
        "status": "acknowledged",
        "message": "A data refresh can be triggered by hitting the primary data endpoints."
    }
    assert response.json() == expected_response
