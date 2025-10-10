# tests/test_legacy_scenarios.py

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, date
from decimal import Decimal

from python_service.models import Race, Runner, OddsData

# Note: The 'client' fixture is automatically available from tests/conftest.py

# --- Mock Data representing historical edge cases from the 'Oracle's Library' ---

def create_mock_runner(number, odds_val, scratched=False):
    """Helper to create a Runner Pydantic model for mock responses."""
    odds_data = {}
    if odds_val:
        odds_data["LegacySource"] = OddsData(
            win=Decimal(odds_val),
            source="LegacySource",
            last_updated=datetime.now()
        )
    return Runner(number=number, name=f"Horse {number}", odds=odds_data, scratched=scratched)

# SCENARIO 1: A race that should PASS all Trifecta criteria
MOCK_RACE_PASS = Race(
    id="LEGACY_PASS_1", venue="Legacy Park", race_number=1, start_time=datetime.now(), source="Legacy",
    runners=[
        create_mock_runner(1, "3.0"), # Favorite > 2.5
        create_mock_runner(2, "4.5"), # 2nd Fav > 4.0
        create_mock_runner(3, "5.0"),
        create_mock_runner(4, "8.0"),
        create_mock_runner(5, "10.0") # Field size < 10
    ]
)

# SCENARIO 2: A race that should FAIL due to a large field size
MOCK_RACE_FAIL_FIELD_SIZE = Race(
    id="LEGACY_FAIL_FS", venue="Legacy Park", race_number=2, start_time=datetime.now(), source="Legacy",
    runners=[create_mock_runner(i, str(5.0 + i)) for i in range(1, 12)] # 11 runners
)

# SCENARIO 3: A race that should FAIL due to low favorite odds
MOCK_RACE_FAIL_FAV_ODDS = Race(
    id="LEGACY_FAIL_FO", venue="Legacy Park", race_number=3, start_time=datetime.now(), source="Legacy",
    runners=[create_mock_runner(1, "2.0"), create_mock_runner(2, "4.5"), create_mock_runner(3, "5.0")]
)

# SCENARIO 4: A race that should FAIL due to low second favorite odds
MOCK_RACE_FAIL_2ND_FAV_ODDS = Race(
    id="LEGACY_FAIL_SFO", venue="Legacy Park", race_number=4, start_time=datetime.now(), source="Legacy",
    runners=[create_mock_runner(1, "3.0"), create_mock_runner(2, "3.5"), create_mock_runner(3, "5.0")]
)


@patch('python_service.engine.OddsEngine.fetch_all_odds', new_callable=AsyncMock)
def test_trifecta_analyzer_with_legacy_scenarios(mock_fetch, client):
    """
    Tests the /api/races/qualified endpoint against a battery of restored legacy scenarios
    to ensure the TrifectaAnalyzer is robust against historical edge cases.
    """
    # ARRANGE
    # The OddsEngine returns a dictionary, so we mock that structure.
    mock_engine_response = {
        "races": [
            MOCK_RACE_PASS,
            MOCK_RACE_FAIL_FIELD_SIZE,
            MOCK_RACE_FAIL_FAV_ODDS,
            MOCK_RACE_FAIL_2ND_FAV_ODDS
        ]
    }
    mock_fetch.return_value = mock_engine_response

    headers = {"X-API-Key": "test_api_key"}
    today = date.today().isoformat()

    # ACT
    response = client.get(f"/api/races/qualified/trifecta?race_date={today}", headers=headers)

    # ASSERT
    assert response.status_code == 200
    response_data = response.json()
    qualified_races = response_data['races']

    # The analyzer should correctly filter the 4 mock races down to the 1 that passes.
    assert len(qualified_races) == 1, "Only one race should have passed the Trifecta criteria"
    assert qualified_races[0]["id"] == "LEGACY_PASS_1"

    # Verify that the criteria are returned in the response as per the 'Analyst's Verdict' mission
    assert 'criteria' in response_data
    assert response_data['criteria']['max_field_size'] == 10

    mock_fetch.assert_awaited_once()