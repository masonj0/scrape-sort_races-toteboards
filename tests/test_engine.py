import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, date
from decimal import Decimal
import fakeredis.aioredis

from python_service.models import Race, Runner, OddsData
from python_service.engine import OddsEngine
from python_service.config import get_settings
from python_service.adapters.base import BaseAdapter

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

    source_a_race = create_mock_race("SourceA", "Test Park", 1, test_time, [
        {"number": 1, "name": "Speedy", "odds": "5.0"},
        {"number": 2, "name": "Steady", "odds": "10.0"},
    ])
    source_b_race = create_mock_race("SourceB", "Test Park", 1, test_time, [
        {"number": 1, "name": "Speedy", "odds": "5.5"},
        {"number": 3, "name": "Newcomer", "odds": "15.0"},
    ])
    other_race = create_mock_race("SourceC", "Another Place", 2, test_time, [
        {"number": 1, "name": "Solo", "odds": "3.0"}
    ])

    mock_time_adapter_fetch.side_effect = [
        ("SourceA", {'races': [source_a_race], 'source_info': {'name': 'SourceA', 'status': 'SUCCESS', 'races_fetched': 1}}, 1.0),
        ("SourceB", {'races': [source_b_race], 'source_info': {'name': 'SourceB', 'status': 'SUCCESS', 'races_fetched': 1}}, 1.0),
        ("SourceC", {'races': [other_race], 'source_info': {'name': 'SourceC', 'status': 'SUCCESS', 'races_fetched': 1}}, 1.0),
    ]

    # ACT
    today_str = date.today().strftime('%Y-%m-%d')
    result = await mock_engine.fetch_all_odds(today_str)

    # ASSERT
    assert len(result['races']) == 2, "Engine should have de-duplicated the races."

    merged_race = next((r for r in result['races'] if r['venue'] == "Test Park"), None)
    assert merged_race is not None, "Merged race should be present in the results."
    assert len(merged_race['runners']) == 3, "Merged race should contain all unique runners."

    runner1 = next((r for r in merged_race['runners'] if r['number'] == 1), None)
    assert runner1 is not None
    assert "SourceA" in runner1['odds']
    assert "SourceB" in runner1['odds']
    assert runner1['odds']['SourceA']['win'] == Decimal("5.0")
    assert runner1['odds']['SourceB']['win'] == Decimal("5.5")

    runner2 = next((r for r in merged_race['runners'] if r['number'] == 2), None)
    assert runner2 is not None
    assert "SourceA" in runner2['odds'] and "SourceB" not in runner2['odds']

    runner3 = next((r for r in merged_race['runners'] if r['number'] == 3), None)
    assert runner3 is not None
    assert "SourceB" in runner3['odds'] and "SourceA" not in runner3['odds']


@pytest.mark.asyncio
@patch('python_service.engine.redis.from_url')
async def test_engine_caching_logic(mock_redis_from_url):
    """
    SPEC: The OddsEngine should cache results in Redis.
    1. On a cache miss, it should fetch from adapters and set the cache.
    2. On a cache hit, it should return data from the cache without fetching from adapters.
    """
    # ARRANGE
    mock_redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    mock_redis_from_url.return_value = mock_redis_client
    await mock_redis_client.flushall()

    engine = OddsEngine(config=get_settings())

    today_str = date.today().strftime('%Y-%m-%d')
    cache_key = f"fortuna:races:{today_str}"
    test_time = datetime(2025, 10, 9, 15, 0)

    mock_race = create_mock_race("TestSource", "Cache Park", 1, test_time, [
        {"number": 1, "name": "Cachedy", "odds": "4.0"}
    ])

    # Replace the engine's adapters with a single mock to isolate the test
    mock_adapter = AsyncMock(spec=BaseAdapter)
    mock_adapter.source_name = "TestSource"
    mock_adapter.fetch_races.return_value = {
        'races': [mock_race],
        'source_info': {'name': 'TestSource', 'status': 'SUCCESS', 'races_fetched': 1}
    }
    engine.adapters = [mock_adapter]


    # --- ACT 1: Cache Miss ---
    result_miss = await engine.fetch_all_odds(today_str)

    # --- ASSERT 1: Cache Miss ---
    mock_adapter.fetch_races.assert_called_once()
    cached_value = await mock_redis_client.get(cache_key)
    assert cached_value is not None
    assert len(result_miss['races']) == 1
    assert result_miss['races'][0]['venue'] == "Cache Park"


    # --- ACT 2: Cache Hit ---
    mock_adapter.fetch_races.reset_mock()
    result_hit = await engine.fetch_all_odds(today_str)

    # --- ASSERT 2: Cache Hit ---
    mock_adapter.fetch_races.assert_not_called()
    assert len(result_hit['races']) == 1
    assert result_hit['races'][0]['venue'] == "Cache Park"

    assert result_hit['races'] == result_miss['races']
    assert result_hit['sources'] == result_miss['sources']

    await engine.close()