# tests/test_api.py

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from decimal import Decimal

from python_service.models import Race, Runner, OddsData, RaceDay

# The 'client' fixture is automatically available from tests/conftest.py

def test_health_check(client):
    """
    SPEC: The /health endpoint should be available and return a healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Patch where the function is LOOKED UP (in the api module), not where it's defined.
@patch('python_service.api.fetch_all_races', new_callable=AsyncMock)
def test_get_races_success(mock_fetch, client):
    """
    SPEC: The /api/races endpoint should return a list of RaceDay objects with a valid API key.
    """
    # ARRANGE
    now = datetime.now()
    mock_raceday = RaceDay(
        track_name="Test Park",
        races=[
            Race(
                id="test_race_1",
                venue="Test Park",
                race_number=1,
                start_time=now,
                runners=[
                    Runner(
                        number=1,
                        name="Test Runner 1",
                        odds={
                            "TestSource": OddsData(
                                win=Decimal("5.0"),
                                source="TestSource",
                                last_updated=now
                            )
                        }
                    )
                ],
                source="TestSource"
            )
        ]
    )
    mock_fetch.return_value = [mock_raceday]
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get("/api/races", headers=headers)

    # ASSERT
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]['track_name'] == "Test Park"
    mock_fetch.assert_awaited_once()

@patch('python_service.api.get_adapter_statuses')
def test_get_all_adapter_statuses_success(mock_get_statuses, client):
    """
    SPEC: The /api/adapters/status endpoint should return status data for all adapters.
    """
    mock_status_data = [
        {'adapter_name': 'AtTheRaces', 'status': 'OK'},
        {'adapter_name': 'BetfairExchange', 'status': 'OK'},
        {'adapter_name': 'BetfairGreyhound', 'status': 'OK'},
        {'adapter_name': 'Harness Racing (USTA)', 'status': 'OK'},
        {'adapter_name': 'Racing and Sports', 'status': 'OK'},
        {'adapter_name': 'Racing and Sports Greyhound', 'status': 'OK'},
        {'adapter_name': 'SportingLife', 'status': 'OK'},
        {'adapter_name': 'Timeform', 'status': 'OK'},
        {'adapter_name': 'TVG', 'status': 'OK'}
    ]
    mock_get_statuses.return_value = mock_status_data
    headers = {"X-API-Key": "test_api_key"}

    response = client.get("/api/adapters/status", headers=headers)

    assert response.status_code == 200
    assert response.json() == mock_status_data
    mock_get_statuses.assert_called_once()

@patch('python_service.api.fetch_all_races', new_callable=AsyncMock)
def test_get_qualified_races_success(mock_fetch, client):
    """
    SPEC: The /api/races/qualified endpoint should correctly filter races.
    """
    # ARRANGE
    now = datetime.now()
    # This race should pass the TrifectaAnalyzer's default criteria
    passing_race = Race(
        id="passing_race", venue="Test Park", race_number=1, start_time=now, source="Test",
        runners=[
            Runner(number=1, name="Fav", odds={"Test": OddsData(win=Decimal("3.0"), source="Test", last_updated=now)}),
            Runner(number=2, name="SecondFav", odds={"Test": OddsData(win=Decimal("4.5"), source="Test", last_updated=now)}),
            Runner(number=3, name="ThirdFav", odds={"Test": OddsData(win=Decimal("5.0"), source="Test", last_updated=now)})
        ]
    )
    # This race should fail because the favorite's odds are too low
    failing_race = Race(
        id="failing_race", venue="Test Park", race_number=2, start_time=now, source="Test",
        runners=[
            Runner(number=1, name="TooHotFav", odds={"Test": OddsData(win=Decimal("1.5"), source="Test", last_updated=now)})
        ]
    )

    mock_fetch.return_value = [RaceDay(track_name="Test Park", races=[passing_race, failing_race])]
    headers = {"X-API-Key": "test_api_key"}

    # ACT
    response = client.get("/api/races/qualified/trifecta", headers=headers)

    # ASSERT
    assert response.status_code == 200
    qualified_races = response.json()
    assert len(qualified_races) == 1
    assert qualified_races[0]['id'] == "passing_race"
    assert 'qualification_score' in qualified_races[0]
    mock_fetch.assert_awaited_once()