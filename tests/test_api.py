# tests/test_api.py

import pytest
import aiosqlite
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

from python_service.models import Race, Runner, OddsData, TipsheetRace

# Note: The 'client' fixture is automatically available from tests/conftest.py

@pytest.mark.asyncio
@patch('python_service.engine.FortunaEngine.get_races', new_callable=AsyncMock)
async def test_get_races_endpoint_success(mock_get_races, client):
    """
    SPEC: The /api/races endpoint should return data with a valid API key.
    """
    # ARRANGE
    today = date.today()
    now = datetime.now()
    mock_response_data = {
        "date": today.isoformat(),
        "races": [],
        "sources": [],
        "metadata": {
            "fetch_time": now.isoformat(),
            "sources_queried": [],
            "sources_successful": 0,
            "total_races": 0
        }
    }
    mock_get_races.return_value = mock_response_data

    # ACT
    response = client.get(f"/api/races?current_date={today.isoformat()}")

    # ASSERT
    assert response.status_code == 200
    assert response.json()["date"] == today.isoformat()
    mock_get_races.assert_awaited_once()

from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_get_tipsheet_endpoint_success():
    """
    SPEC: The /api/tipsheet endpoint should return a list of tipsheet races from the database.
    This test now uses a real in-memory database and correctly triggers the lifespan events.
    """
    db_path = ":memory:"
    post_time = datetime.now()

    with patch('python_service.api.DB_PATH', db_path):
        from python_service.api import app
        with TestClient(app) as client:
            # The lifespan startup event has now run, creating the table.
            # Now we can connect to the same in-memory DB to insert our test data.
            async with aiosqlite.connect(db_path) as db:
                await db.execute(
                    "INSERT INTO tipsheet VALUES (?, ?, ?, ?, ?, ?)",
                    ("test_race_1", "Test Park", 1, post_time.isoformat(), 85.5, "{}")
                )
                await db.commit()

            # ACT
            response = client.get(f"/api/tipsheet?date={post_time.date().isoformat()}")

            # ASSERT
            assert response.status_code == 200
            response_data = response.json()
            assert len(response_data) == 1
            assert response_data[0]["race_id"] == "test_race_1"
            assert response_data[0]["score"] == 85.5