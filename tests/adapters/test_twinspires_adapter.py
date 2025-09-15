#!/usr/bin/env python3
"""
A V3-compliant test suite for the two-stage TwinSpires adapter.
This test correctly mocks both stages of the fetch process.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from paddock_parser.adapters.twinspires_adapter import TwinSpiresAdapter

# Helper function to load mock data from files
def load_mock_data(file_name: str) -> str:
    """Loads mock HTML data from the specified file."""
    path = Path(__file__).parent / "mock_data" / file_name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def twinspires_adapter():
    """Provides a fresh instance of the adapter for each test."""
    return TwinSpiresAdapter()

import sys

@pytest.mark.anyio
@patch('paddock_parser.adapters.twinspires_adapter.get_page_content')
async def test_twinspires_adapter_full_two_stage_fetch(mock_get_page, twinspires_adapter):
    """
    Tests the full, two-stage fetch and parse process.
    Mocks the return value of get_page_content to simulate the two different pages.
    """
    if 'trio' in sys.modules:
        pytest.skip("Skipping skysports test on trio due to asyncio.gather conflict.")

    # Load the mock HTML for both stages
    index_html = load_mock_data("twinspires_index_sample.html")
    detail_html = load_mock_data("twinspires_detail_sample.html")

    # Configure the mock to return the index page on the first call,
    # and the detail page on the second call.
    mock_get_page.side_effect = [
        index_html,  # First call to fetch() gets the index
        detail_html  # Second call (inside the asyncio.gather) gets the detail
    ]

    # --- ACT ---
    # Run the adapter's fetch method
    races = await twinspires_adapter.fetch()

    # --- ASSERT ---
    # 1. Verify the network calls
    assert mock_get_page.call_count == 2, "Should have made two calls: one for index, one for detail"

    # 2. Verify the parsed data
    assert len(races) == 1, "Should have parsed exactly one race from the mock data"

    race = races[0]
    assert race.track == "FAIR GROUNDS", "Track name should be parsed correctly"
    assert race.race_number == 1, "Race number should be parsed correctly"

    assert len(race.runners) > 0, "Should have parsed runners"
    assert race.runners[0].name == "Fierce Warrior", "First runner's name should be correct"
