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
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get(f"/api/races?date={today.isoformat()}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    assert response.json()["date"] == today.isoformat()
    mock_get_races.assert_awaited_once()