"""
Test-as-Spec for the API Exporter Endpoints
Path: tests/api/test_exporters.py
"""

import pytest
import csv
from io import StringIO
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import datetime

# Assume these data structures will be imported from the project
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

# The FastAPI app
from src.paddock_parser.api.main import app

# Create a TestClient instance for making API requests in tests
client = TestClient(app)

@pytest.fixture
def mock_pipeline_data():
    """Provides a sample list of NormalizedRace objects for mocking."""
    # This is duplicated from test_main.py for simplicity.
    # In a larger project, this could be moved to a shared conftest.py
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

class TestExporterEndpoints:
    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_get_races_json_endpoint(self, mock_run_pipeline, mock_pipeline_data):
        """
        SPEC: The /api/v1/races.json endpoint should return a JSON array of race objects,
        behaving identically to the main /api/v1/races endpoint.
        """
        mock_run_pipeline.return_value = mock_pipeline_data

        response = client.get("/api/v1/races.json")

        assert response.status_code == 200
        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 2
        assert response_data[0]["race_id"] == "AQU_20250901_1"
        assert response_data[1]["track_name"] == "Santa Anita"

    @patch('src.paddock_parser.api.main.run_pipeline')
    def test_get_races_csv_endpoint(self, mock_run_pipeline, mock_pipeline_data):
        """
        SPEC: The /api/v1/races.csv endpoint should return race data as a CSV file.
        """
        mock_run_pipeline.return_value = mock_pipeline_data

        response = client.get("/api/v1/races.csv")

        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/csv; charset=utf-8'

        # Parse the CSV content
        csv_content = response.text
        reader = csv.reader(StringIO(csv_content))

        rows = list(reader)

        # Check header
        expected_header = ["race_id", "track_name", "race_number", "post_time", "number_of_runners", "score"]
        assert rows[0] == expected_header

        # Check data rows
        assert len(rows) == 3 # 1 header + 2 data rows

        # Check first data row content
        assert rows[1][0] == "AQU_20250901_1"
        assert rows[1][1] == "Aqueduct"
        assert rows[1][2] == "1"
        assert rows[1][3] == "2025-09-01T13:00:00"
        assert rows[1][4] == "8"
        assert rows[1][5] == "95"

        # Check second data row content
        assert rows[2][0] == "SA_20250901_3"
        assert rows[2][1] == "Santa Anita"
