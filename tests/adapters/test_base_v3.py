# tests/adapters/test_base_v3.py
import pytest
from typing import Any, List
from python_service.adapters.base_v3 import BaseAdapterV3
from python_service.models import Race

# A concrete implementation for testing the abstract class
class ConcreteAdapter(BaseAdapterV3):
    def __init__(self, source_name: str, base_url: str):
        super().__init__(source_name, base_url)

    SOURCE_NAME = "TestAdapter"
    async def _fetch_data(self, date: str) -> Any:
        if date == "good_data":
            return [{"id": 1}, {"id": 2}]
        if date == "no_data":
            return None
        if date == "bad_data":
            raise ValueError("Simulated fetch error")
        return None

    def _parse_races(self, raw_data: Any) -> List[Race]:
        # In a real test, you'd mock Race objects
        return raw_data # Simple passthrough for testing orchestration

    async def fetch_races(self, date: str, http_client):
        pass

@pytest.mark.asyncio
async def test_get_races_orchestration_success():
    """Tests that _fetch_data and _parse_races are called in order on success."""
    adapter = ConcreteAdapter(source_name="TestAdapter", base_url="http://test.com")
    races = [race async for race in adapter.get_races("good_data")]
    assert len(races) == 2
    assert races == [{"id": 1}, {"id": 2}]
    assert adapter.circuit_breaker_failure_count == 0

@pytest.mark.asyncio
async def test_get_races_handles_no_data_from_fetch():
    """Tests that the pipeline gracefully exits if _fetch_data returns None."""
    adapter = ConcreteAdapter(source_name="TestAdapter", base_url="http://test.com")
    races = [race async for race in adapter.get_races("no_data")]
    assert len(races) == 0

@pytest.mark.asyncio
async def test_get_races_handles_fetch_exception_and_trips_breaker():
    """Tests that an exception in _fetch_data is caught and trips the circuit breaker."""
    adapter = ConcreteAdapter(source_name="TestAdapter", base_url="http://test.com")
    assert not adapter.circuit_breaker_tripped

    # Fail 3 times to trip the breaker
    for _ in range(3):
        races = [race async for race in adapter.get_races("bad_data")]
        assert len(races) == 0

    assert adapter.circuit_breaker_tripped
    assert adapter.circuit_breaker_failure_count == 3

    # On the 4th attempt, it should not even try to fetch
    races = [race async for race in adapter.get_races("good_data")]
    assert len(races) == 0