import pytest
from src.checkmate_v7 import services

@pytest.mark.anyio
async def test_data_source_orchestrator():
    """Tests the data source orchestrator."""
    orchestrator = services.DataSourceOrchestrator()
    data = await orchestrator.get_race_data()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['source'] == 'twinspires'
