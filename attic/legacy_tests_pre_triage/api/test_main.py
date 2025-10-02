"""
Test-as-Spec for the FastAPI Server
Path: tests/api/test_main.py
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import datetime

# Assume these data structures will be imported from the project
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

# The yet-to-be-created FastAPI app
from src.paddock_parser.api.main import app

# Create a TestClient instance for making API requests in tests
client = TestClient(app)

@pytest.fixture
def mock_pipeline_data():
    """Provides a sample list of NormalizedRace objects for mocking."""
    return [
        NormalizedRace(
            race_id="AQU_20250901_1",
            track_name="Aqueduct",
            race_number=1,
            post_time=datetime(2025, 9, 1, 13, 0, 0),
            number_of_runners=8,
            runners=[
                NormalizedRunner(name="Speedster", program_number=1),
                NormalizedRunner(name="Galloper", program_number=2),
            ],
            score=95,
        ),
        NormalizedRace(
            race_id="SA_20250901_3",
            track_name="Santa Anita",
            race_number=3,
            post_time=datetime(2025, 9, 1, 15, 30, 0),
            number_of_runners=10,
            runners=[],
            score=110,
        ),
    ]

class TestAPIRoot:
    def test_read_root_returns_welcome_message(self):
        """
        SPEC: The root endpoint ("/") should exist and return a simple welcome message.
        This confirms the API is running and responsive.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Paddock Parser API is running."}

class TestRacesEndpoint:
    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_get_races_returns_200_ok(self, mock_run_pipeline):
        """
        SPEC: The /api/v1/races endpoint should exist and return a 200 OK status code.
        """
        mock_run_pipeline.return_value = []  # Return empty list for this test
        response = client.get("/api/v1/races")
        assert response.status_code == 200

    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_get_races_returns_list_of_races(self, mock_run_pipeline, mock_pipeline_data):
        """
        SPEC: The /api/v1/races endpoint should return a JSON array of race objects
        that match the data returned from the pipeline.
        """
        mock_run_pipeline.return_value = mock_pipeline_data

        response = client.get("/api/v1/races")

        assert response.status_code == 200
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 2
        assert response_data[0]["track_name"] == "Aqueduct"
        assert response_data[1]["track_name"] == "Santa Anita"

    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_race_schema_is_correct(self, mock_run_pipeline, mock_pipeline_data):
        """
        SPEC: The JSON objects returned should conform to the Pydantic schema,
        including correct data types and nested runner objects.
        """
        mock_run_pipeline.return_value = mock_pipeline_data

        response = client.get("/api/v1/races")
        response_data = response.json()

        first_race = response_data[0]

        # Verify data types and structure
        assert isinstance(first_race["race_id"], str)
        assert first_race["race_id"] == "AQU_20250901_1"
        assert isinstance(first_race["track_name"], str)
        assert isinstance(first_race["race_number"], int)
        assert isinstance(first_race["post_time"], str) # Pydantic converts datetime to ISO string
        assert first_race["post_time"] == "2025-09-01T13:00:00"
        assert isinstance(first_race["number_of_runners"], int)
        assert isinstance(first_race["score"], int)

        # Verify nested runners schema
        assert isinstance(first_race["runners"], list)
        assert len(first_race["runners"]) == 2
        assert first_race["runners"][0]["name"] == "Speedster"

    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_pipeline_is_called_with_default_parameters(self, mock_run_pipeline):
        """
        SPEC: The endpoint should call the core run_pipeline function
        with default parameters if none are provided in the request.
        """
        mock_run_pipeline.return_value = []

        client.get("/api/v1/races")

        # Verify that the backend logic was called correctly
        mock_run_pipeline.assert_called_once()
        # Check that it was called with default arguments
        args, kwargs = mock_run_pipeline.call_args
        assert kwargs.get('min_runners') is None # Or whatever the default is
        assert kwargs.get('specific_source') is None

    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_pipeline_is_called_with_query_parameters(self, mock_run_pipeline):
        """
        SPEC: The endpoint can accept query parameters to filter the pipeline run.
        e.g., /api/v1/races?min_runners=10&source=equibase
        """
        mock_run_pipeline.return_value = []

        client.get("/api/v1/races?min_runners=10&source=equibase")

        mock_run_pipeline.assert_called_once()
        args, kwargs = mock_run_pipeline.call_args

        # Verify that the query parameters were passed to the backend function
        assert kwargs.get('min_runners') == 10
        assert kwargs.get('specific_source') == 'equibase'
