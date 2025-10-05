import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

# Note: The 'client' fixture is automatically available from tests/conftest.py

# --- Mock Data for "True Trifecta" Logic ---
# This data is structured to test the new analyzer's specific rules.

def create_mock_runner(number, odds_val):
    """Helper to create a runner dictionary for mock responses."""
    return {
        "number": number,
        "name": f"Horse {number}",
        "scratched": False,
        "odds": {"TestOdds": {"win": odds_val, "source": "TestOdds", "last_updated": datetime.now().isoformat()}}
    }

# This race should PASS: 5 runners (<10), fav odds 3.0 (>2.5), 2nd fav odds 4.5 (>4.0)
MOCK_RACE_PASS_TT = {
    "id": "TT_PASS_1", "venue": "Trifecta Park", "race_number": 1, "start_time": datetime.now().isoformat(), "source": "Legacy",
    "runners": [
        create_mock_runner(1, "3.0"), create_mock_runner(2, "4.5"), create_mock_runner(3, "5.0"),
        create_mock_runner(4, "8.0"), create_mock_runner(5, "10.0")
    ]
}

# This race should FAIL: Field size is 11 (> 10)
MOCK_RACE_FAIL_FIELD_SIZE_TT = {
    "id": "TT_FAIL_FS", "venue": "Trifecta Park", "race_number": 2, "start_time": datetime.now().isoformat(), "source": "Legacy",
    "runners": [create_mock_runner(i, str(5.0 + i)) for i in range(1, 12)]
}

# This race should FAIL: Favorite odds are 2.0 (< 2.5)
MOCK_RACE_FAIL_FAV_ODDS_TT = {
    "id": "TT_FAIL_FO", "venue": "Trifecta Park", "race_number": 3, "start_time": datetime.now().isoformat(), "source": "Legacy",
    "runners": [create_mock_runner(1, "2.0"), create_mock_runner(2, "4.5"), create_mock_runner(3, "5.0")]
}

# This race should FAIL: Second favorite odds are 3.5 (< 4.0)
MOCK_RACE_FAIL_2ND_FAV_ODDS_TT = {
    "id": "TT_FAIL_SFO", "venue": "Trifecta Park", "race_number": 4, "start_time": datetime.now().isoformat(), "source": "Legacy",
    "runners": [create_mock_runner(1, "3.0"), create_mock_runner(2, "3.5"), create_mock_runner(3, "5.0")]
}


@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_true_trifecta_analyzer_with_legacy_scenarios(mock_fetch, client):
    """
    Tests the /api/races/qualified endpoint against legacy scenarios adapted
    for the new 'True Trifecta' logic.
    """
    # ARRANGE
    mock_engine_response = {
        "races": [
            MOCK_RACE_PASS_TT,
            MOCK_RACE_FAIL_FIELD_SIZE_TT,
            MOCK_RACE_FAIL_FAV_ODDS_TT,
            MOCK_RACE_FAIL_2ND_FAV_ODDS_TT
        ]
    }
    mock_fetch.return_value = mock_engine_response

    headers = {"X-API-Key": "test_api_key"}
    today = date.today().isoformat()

    # ACT
    response = client.get(f"/api/races/qualified/trifecta?race_date={today}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    qualified_races = response.json()

    # The analyzer should filter the 4 mock races down to the 1 that passes
    assert len(qualified_races) == 1, "Only one race should have passed the True Trifecta criteria"
    assert qualified_races[0]["id"] == "TT_PASS_1"
    mock_fetch.assert_awaited_once()