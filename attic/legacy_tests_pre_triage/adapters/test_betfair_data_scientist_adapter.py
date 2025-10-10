import pytest
from unittest.mock import patch

from src.paddock_parser.adapters.betfair_data_scientist_adapter import BetfairDataScientistAdapter

@pytest.fixture
def sample_csv_data():
    """Sample CSV data from the Betfair Data Scientist API."""
    csv_data = """market_id,selection_id,meetings.races.runners.ratedPrice
1.234,5678,1.5
1.234,5679,2.5
1.235,5680,3.0
"""
    return csv_data

@pytest.mark.anyio
@patch("src.paddock_parser.adapters.betfair_data_scientist_adapter.get_page_content")
async def test_betfair_adapter_fetches_and_parses(mock_get_page_content, sample_csv_data):
    """
    Tests that the BetfairDataScientistAdapter correctly fetches, parses,
    and normalizes data from the CSV API.
    """
    mock_get_page_content.return_value = sample_csv_data

    adapter = BetfairDataScientistAdapter()
    races = await adapter.fetch()

    mock_get_page_content.assert_called_once()
    assert "presenter=RatingsPresenter" in mock_get_page_content.call_args[0][0]
    assert "csv=true" in mock_get_page_content.call_args[0][0]

    assert len(races) == 2  # Two unique market_ids

    race1 = next((r for r in races if r.race_id == "1.234"), None)
    assert race1 is not None
    assert len(race1.runners) == 2
    assert race1.runners[0].name == "5678"
    assert race1.runners[0].odds == 1.5
    assert race1.runners[1].name == "5679"
    assert race1.runners[1].odds == 2.5

    race2 = next((r for r in races if r.race_id == "1.235"), None)
    assert race2 is not None
    assert len(race2.runners) == 1
    assert race2.runners[0].name == "5680"
    assert race2.runners[0].odds == 3.0
