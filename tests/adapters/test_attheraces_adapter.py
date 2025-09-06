import pytest
from datetime import datetime

from paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter
from paddock_parser.base import NormalizedRace, NormalizedRunner

@pytest.fixture
def real_attheraces_html():
    """
    Fixture providing actual At The Races HTML structure.
    Based on https://www.attheraces.com/racecard/Roscommon/01-September-2025/1745
    """
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <div class="race-header"><h1>17:45 Roscommon (IRE) 01 Sep 2025</h1><div class="race-info"><div>Lecarrow Race</div></div></div>
        <div class="runner-card" data-horse="In My Teens"><div class="runner-info"><div class="horse-name"><a>In My Teens</a></div><div class="runner-number">72</div><div class="connections"><div class="jockey">J: G F Carroll</div><div class="trainer">T: G P Cromwell</div></div><div class="odds">7/2</div></div></div>
        <div class="runner-card" data-horse="Vorfreude"><div class="runner-info"><div class="horse-name"><a>Vorfreude</a></div><div class="runner-number">11</div><div class="connections"><div class="jockey">J: B M Coen</div><div class="trainer">T: J G Murphy</div></div><div class="odds">11/4</div></div></div>
    </body>
    </html>
    """

def test_parse_races_extracts_correct_data(real_attheraces_html):
    """
    Tests that the adapter correctly parses the HTML and extracts all runner and race data.
    """
    adapter = AtTheRacesAdapter()
    races = adapter.parse_races(real_attheraces_html)

    assert len(races) == 1
    race = races[0]

    assert race.track_name == "Roscommon (IRE)"
    assert race.post_time == datetime(2025, 9, 1, 17, 45)
    assert race.race_type == "Lecarrow Race"
    assert race.number_of_runners == 2

    assert len(race.runners) == 2

    in_my_teens = race.runners[0]
    assert in_my_teens.name == "In My Teens"
    assert in_my_teens.program_number == 72
    assert in_my_teens.jockey == "G F Carroll"
    assert in_my_teens.trainer == "G P Cromwell"
    assert in_my_teens.odds == 4.5 # 7/2 + 1

    vorfreude = race.runners[1]
    assert vorfreude.name == "Vorfreude"
    assert vorfreude.program_number == 11
    assert vorfreude.jockey == "B M Coen"
    assert vorfreude.trainer == "J G Murphy"
    assert vorfreude.odds == 3.75 # 11/4 + 1
