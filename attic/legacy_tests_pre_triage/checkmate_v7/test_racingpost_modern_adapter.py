import pytest
from unittest.mock import MagicMock

from src.checkmate_v7.adapters.AndWereOff import SkySportsAdapter as RacingPostModernAdapter
from src.checkmate_v7.base import DefensiveFetcher

# --- Fixtures ---

@pytest.fixture
def mock_fetcher():
    """Provides a MagicMock for the DefensiveFetcher."""
    return MagicMock(spec=DefensiveFetcher)

@pytest.fixture
def adapter(mock_fetcher):
    """Provides an adapter instance with a mocked fetcher."""
    return RacingPostModernAdapter(mock_fetcher)

@pytest.fixture
def mock_html_data():
    """Provides mock HTML data for a racecard."""
    # This is a simplified version of the HTML structure
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Racecard</title>
    </head>
    <body>
        <h1 class="sdc-site-racing-header__title">Test Track</h1>
        <span class="sdc-site-racing-header__time">13:50</span>
        <div class="sdc-site-racing-card__item">
            <div class="sdc-site-racing-card__number"><strong>1</strong></div>
            <h4 class="sdc-site-racing-card__name"><a href="#">Horse One</a></h4>
            <span class="sdc-site-racing-card__betting-odds">5/1</span>
        </div>
        <div class="sdc-site-racing-card__item">
            <div class="sdc-site-racing-card__number"><strong>2</strong></div>
            <h4 class="sdc-site-racing-card__name"><a href="#">Horse Two</a></h4>
            <span class="sdc-site-racing-card__betting-odds">EVS</span>
        </div>
    </body>
    </html>
    """

# --- Tests ---

def test_fetch_races_end_to_end(adapter, mock_fetcher, mock_html_data):
    """
    Tests the end-to-end flow of the fetch_races method, mocking the fetcher call.
    """
    # Given
    mock_fetcher.get.side_effect = ['<a class="sdc-site-racing-meetings__event-link" href="/racing/racecards/test/2025-09-25/12345"></a>', mock_html_data]

    # When
    races = adapter.fetch_races()

    # Then
    assert mock_fetcher.get.call_count == 2
    assert len(races) == 1
    assert races[0].track_name == "Test Track"
    assert len(races[0].runners) == 2
    assert races[0].runners[0].name == "Horse One"
    assert races[0].runners[0].odds == 6.0
    assert races[0].runners[1].name == "Horse Two"
    assert races[0].runners[1].odds == 2.0