import pytest
from unittest.mock import patch
from src.paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter

@pytest.fixture
def mock_race_card_html():
    return """
    <section class="panel">
        <h2 class="h6">Lingfield Park Racecards</h2>
        <div class="meeting-list-entry">
            <a href="/racecard/Lingfield/1/2025-09-08" class="a--plain">
                <span class="post__number">1</span>
                <span class="h7">13:50 - Sky Sports Racing Open Maiden</span>
            </a>
        </div>
    </section>
    """

@pytest.fixture
def mock_race_page_html():
    return """
    <div class="race-header"><h1>13:50 Lingfield Park 08 Sep 2025</h1></div>
    <div class="race-info"><div>(4yo+, 6f)</div></div>
    <div class="runner-card">
        <div class="runner-number">1</div>
        <div class="horse-name"><a>Horse One</a></div>
        <div class="odds">5/1</div>
    </div>
    <div class="runner-card">
        <div class="runner-number">2</div>
        <div class="horse-name"><a>Horse Two</a></div>
        <div class="odds">EVS</div>
    </div>
    """

@pytest.mark.anyio
@patch('src.paddock_parser.adapters.attheraces_adapter.get_page_content')
async def test_fetch_e2e(mock_get_page_content, mock_race_card_html, mock_race_page_html):
    """
    SPEC: Full end-to-end test of the fetch method.
    """
    # Mock the two calls to get_page_content
    mock_get_page_content.side_effect = [
        mock_race_card_html,
        mock_race_page_html
    ]

    adapter = AtTheRacesAdapter()
    races = await adapter.fetch()

    assert len(races) == 1
    race = races[0]
    assert race.track_name == "Lingfield Park"
    assert race.race_number == 1
    assert race.number_of_runners == 2
    assert race.runners[0].name == "Horse One"
    assert race.runners[0].odds == pytest.approx(6.0)
    assert race.runners[1].name == "Horse Two"
    assert race.runners[1].odds == pytest.approx(2.0)

def test_parse_races_is_not_supported(mock_race_page_html):
    """
    SPEC: This adapter does not support offline parsing.
    """
    adapter = AtTheRacesAdapter()
    races = adapter.parse_races(mock_race_page_html)
    assert races == []
