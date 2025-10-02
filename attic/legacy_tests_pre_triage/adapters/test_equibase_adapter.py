import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from src.paddock_parser.adapters.equibase_adapter import EquibaseAdapter

@pytest.fixture
def adapter():
    return EquibaseAdapter()

@pytest.fixture
def sample_html():
    with open("tests/adapters/mock_data/equibase_test_sample.html", "r") as f:
        return f.read()

def test_parse_race_schedule(adapter, sample_html):
    """
    Tests that the parse_races method correctly extracts race numbers and track names
    from the sample HTML.
    """
    races = adapter.parse_races(sample_html)

    assert len(races) == 3

    assert races[0].track == "Saratoga"
    assert races[0].race_number == 1

    assert races[1].track == "Saratoga"
    assert races[1].race_number == 2

    assert races[2].track == "Gulfstream Park"
    assert races[2].race_number == 8

@patch('src.paddock_parser.adapters.equibase_adapter.get_page_content')
def test_fetch_races(mock_get_page_content, adapter, sample_html):
    """
    Tests that the fetch method correctly calls get_page_content and
    the parse_races method.
    """
    # Create an async mock for get_page_content
    async_mock = MagicMock()
    async_mock.return_value = sample_html
    mock_get_page_content.return_value = async_mock()

    # Since fetch is async, we need to run it in an event loop.
    # Pytest-asyncio would handle this automatically, but we can do it manually.
    import asyncio
    fetch_date = date(2025, 8, 22)
    races = asyncio.run(adapter.fetch(fetch_date))

    # Verify get_page_content was called with the correct URL
    expected_url = "http://www.equibase.com/entries/ENT_082225.html?COUNTRY=USA"
    mock_get_page_content.assert_called_once_with(expected_url)

    # Verify the parsing result
    assert len(races) == 3
    assert races[0].track == "Saratoga"
    assert races[2].race_number == 8

def test_parse_with_no_content(adapter):
    """
    Tests that the parser returns an empty list when given no HTML content.
    """
    races = adapter.parse_races("")
    assert len(races) == 0

@patch('src.paddock_parser.adapters.equibase_adapter.get_page_content')
def test_fetch_with_no_content(mock_get_page_content, adapter):
    """
    Tests that fetch returns an empty list if no content is retrieved.
    """
    async_mock = MagicMock()
    async_mock.return_value = None
    mock_get_page_content.return_value = async_mock()

    import asyncio
    fetch_date = date(2025, 8, 22)
    races = asyncio.run(adapter.fetch(fetch_date))

    assert len(races) == 0
