import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

# Note: The 'client' fixture is automatically available from tests/conftest.py

# Mock data ported from legacy tests, but adapted for modern Pydantic models.
# The structure now matches python_service/models.py exactly.
MOCK_RACE_PASS = {
    "id": "LEGACY_PASS_1",
    "venue": "Legacy Park",
    "race_number": 1,
    "start_time": datetime.now().isoformat(),
    "source": "Legacy",
    "runners": [
        {"number": 1, "name": "Horse A", "scratched": False, "odds": {"TestOdds": {"win": Decimal("2.5"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 2, "name": "Horse B", "scratched": False, "odds": {"TestOdds": {"win": Decimal("3.5"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 3, "name": "Horse C", "scratched": False, "odds": {"TestOdds": {"win": Decimal("4.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 4, "name": "Horse D", "scratched": False, "odds": {"TestOdds": {"win": Decimal("8.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 5, "name": "Horse E", "scratched": False, "odds": {"TestOdds": {"win": Decimal("10.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 6, "name": "Horse F", "scratched": False, "odds": {"TestOdds": {"win": Decimal("12.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 7, "name": "Horse G", "scratched": False, "odds": {"TestOdds": {"win": Decimal("15.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 8, "name": "Horse H", "scratched": False, "odds": {"TestOdds": {"win": Decimal("20.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
    ]
}

MOCK_RACE_FAIL_RUNNERS = {
    "id": "LEGACY_FAIL_1",
    "venue": "Legacy Park",
    "race_number": 2,
    "start_time": datetime.now().isoformat(),
    "source": "Legacy",
    "runners": [
        {"number": i, "name": f"Horse {i}", "scratched": False, "odds": {}} for i in range(1, 8) # Only 7 runners
    ]
}

MOCK_RACE_FAIL_ODDS = {
    "id": "LEGACY_FAIL_2",
    "venue": "Legacy Park",
    "race_number": 3,
    "start_time": datetime.now().isoformat(),
    "source": "Legacy",
    "runners": [
        {"number": 1, "name": "Horse J", "scratched": False, "odds": {"TestOdds": {"win": Decimal("1.5"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}}, # Favorite odds too low
        {"number": 2, "name": "Horse K", "scratched": False, "odds": {"TestOdds": {"win": Decimal("3.5"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 3, "name": "Horse L", "scratched": False, "odds": {"TestOdds": {"win": Decimal("4.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 4, "name": "Horse M", "scratched": False, "odds": {"TestOdds": {"win": Decimal("8.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 5, "name": "Horse N", "scratched": False, "odds": {"TestOdds": {"win": Decimal("10.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 6, "name": "Horse O", "scratched": False, "odds": {"TestOdds": {"win": Decimal("12.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 7, "name": "Horse P", "scratched": False, "odds": {"TestOdds": {"win": Decimal("15.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
        {"number": 8, "name": "Horse Q", "scratched": False, "odds": {"TestOdds": {"win": Decimal("20.0"), "source": "TestOdds", "last_updated": datetime.now().isoformat()}}},
    ]
}

@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_analyzer_with_legacy_scenarios(mock_fetch, client):
    """
    Tests the /api/races/qualified endpoint against ported legacy test cases
    to ensure the TrifectaAnalyzer logic is correctly filtering races.
    """
    # ARRANGE
    # Mock the engine's return value, ensuring it matches the AggregatedResponse structure
    mock_engine_response = {
        "races": [MOCK_RACE_PASS, MOCK_RACE_FAIL_RUNNERS, MOCK_RACE_FAIL_ODDS]
    }
    mock_fetch.return_value = mock_engine_response

    # The API key is mocked in the settings via the conftest.py fixture
    headers = {"X-API-Key": "test_api_key"}
    today = date.today().isoformat()

    # ACT
    response = client.get(f"/api/races/qualified?race_date={today}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    qualified_races = response.json()

    # The analyzer should filter the 3 mock races down to the 1 that passes
    assert len(qualified_races) == 1
    assert qualified_races[0]["id"] == "LEGACY_PASS_1"
    mock_fetch.assert_awaited_once()