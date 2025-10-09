import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, date
from decimal import Decimal

from python_service.models import Race, Runner, OddsData
from python_service.engine import OddsEngine
from python_service.config import get_settings

def create_mock_race(source: str, venue: str, race_number: int, start_time: datetime, runners_data: list) -> Race:
    """Helper function to create a Race object for testing."""
    runners = []
    for r_data in runners_data:
        odds = {source: OddsData(win=Decimal(r_data["odds"]), source=source, last_updated=datetime.now())}
        runners.append(Runner(number=r_data["number"], name=r_data["name"], odds=odds))

    return Race(
        id=f"test_{source}_{race_number}",
        venue=venue,
        race_number=race_number,
        start_time=start_time,
        runners=runners,
        source=source
    )

@pytest.fixture
def mock_engine() -> OddsEngine:
    """Provides an OddsEngine instance with a mock config."""
    return OddsEngine(config=get_settings())

@pytest.mark.asyncio
@patch('python_service.engine.OddsEngine._time_adapter_fetch', new_callable=AsyncMock)
async def test_engine_deduplicates_races_and_merges_odds(mock_time_adapter_fetch, mock_engine):
    """
    SPEC: The OddsEngine's fetch_all_odds method should identify duplicate races
    from different sources and merge their runner data, stacking the odds.
    """
    # ARRANGE
    test_time = datetime(2025, 10, 9, 14, 30)

    # Race data from Source A
    source_a_race = create_mock_race("SourceA", "Test Park", 1, test_time, [
        {"number": 1, "name": "Speedy", "odds": "5.0"},
        {"number": 2, "name": "Steady", "odds": "10.0"},
    ])

    # The same race from Source B, with different odds and an extra runner
    source_b_race = create_mock_race("SourceB", "Test Park", 1, test_time, [
        {"number": 1, "name": "Speedy", "odds": "5.5"}, # Different odds for existing runner
        {"number": 3, "name": "Newcomer", "odds": "15.0"}, # A new runner
    ])

    # A completely different race
    other_race = create_mock_race("SourceC", "Another Place", 2, test_time, [
        {"number": 1, "name": "Solo", "odds": "3.0"}
    ])

    # Mock the return value of the internal fetch method
    mock_time_adapter_fetch.side_effect = [
        ("SourceA", {'races': [source_a_race], 'source_info': {'name': 'SourceA', 'status': 'SUCCESS'}}, 1.0),
        ("SourceB", {'races': [source_b_race], 'source_info': {'name': 'SourceB', 'status': 'SUCCESS'}}, 1.0),
        ("SourceC", {'races': [other_race], 'source_info': {'name': 'SourceC', 'status': 'SUCCESS'}}, 1.0),
    ]

    # ACT
    today_str = date.today().strftime('%Y-%m-%d')
    result = await mock_engine.fetch_all_odds(today_str)

    # ASSERT

    # 1. The total number of races should be 2 after de-duplication
    assert len(result['races']) == 2, "Engine should have de-duplicated the races."

    # 2. Find the merged race and verify its contents
    merged_race = next((r for r in result['races'] if r.venue == "Test Park"), None)
    assert merged_race is not None, "Merged race should be present in the results."

    # 3. Check that the merged race has the correct number of runners (2 from A + 1 new from B)
    assert len(merged_race.runners) == 3, "Merged race should contain all unique runners."

    # 4. Verify that the odds have been stacked correctly for the overlapping runner
    runner1 = next((r for r in merged_race.runners if r.number == 1), None)
    assert runner1 is not None
    assert "SourceA" in runner1.odds
    assert "SourceB" in runner1.odds
    assert runner1.odds["SourceA"].win == Decimal("5.0")
    assert runner1.odds["SourceB"].win == Decimal("5.5")

    # 5. Verify the other runners are present with their correct odds
    runner2 = next((r for r in merged_race.runners if r.number == 2), None)
    assert runner2 is not None
    assert "SourceA" in runner2.odds and "SourceB" not in runner2.odds

    runner3 = next((r for r in merged_race.runners if r.number == 3), None)
    assert runner3 is not None
    assert "SourceB" in runner3.odds and "SourceA" not in runner3.odds