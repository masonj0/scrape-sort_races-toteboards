# Modernized test resurrected from attic/legacy_tests_pre_triage/adapters/test_timeform_adapter.py
import pytest
from unittest.mock import MagicMock, patch
import httpx
from decimal import Decimal
from python_service.adapters.timeform_adapter import TimeformAdapter
from python_service.models import Race, Runner

@pytest.fixture
def timeform_adapter():
    mock_config = MagicMock()
    return TimeformAdapter(config=mock_config)

def read_fixture(file_path):
    with open(file_path, 'r') as f:
        return f.read()

@pytest.mark.asyncio
async def test_timeform_adapter_parses_html_correctly(timeform_adapter):
    """Verify adapter correctly parses a known HTML fixture."""
    mock_html = read_fixture('tests/fixtures/timeform_modern_sample.html')

    # Directly test the parsing of runners from the correct HTML structure
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mock_html, "html.parser")
    runners = [timeform_adapter._parse_runner(row) for row in soup.select("div.rp-horseTable_mainRow")]

    assert len(runners) == 3, 'Should parse three runners'

    braveheart = next((r for r in runners if r.name == 'Braveheart'), None)
    assert braveheart is not None
    assert braveheart.odds['Timeform'].win == Decimal('3.5')

    steady_eddy = next((r for r in runners if r.name == 'Steady Eddy'), None)
    assert steady_eddy is not None
    assert steady_eddy.odds['Timeform'].win == Decimal('2.0')