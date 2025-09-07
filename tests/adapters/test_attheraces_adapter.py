import asyncio
import os
from unittest.mock import patch

import pytest
from paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter
from paddock_parser.base import NormalizedRace, NormalizedRunner


@pytest.fixture
def adapter():
    return AtTheRacesAdapter()


@pytest.fixture
def attheraces_racecards_html():
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "attheraces_racecards.html"), "r") as f:
        return f.read()


@pytest.fixture
def attheraces_race_html():
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "attheraces_race.html"), "r") as f:
        return f.read()


def test_get_race_details(adapter, attheraces_racecards_html):
    race_details = adapter._get_race_details(attheraces_racecards_html)
    assert len(race_details) == 1
    assert race_details[0]["course"] == "Fontwell"
    assert race_details[0]["time"] == "14:12"
    assert "Southern Cranes" in race_details[0]["name"]
    assert race_details[0]["url"] == "https://www.attheraces.com/racecard/Fontwell/07-September-2025/1412"
    assert race_details[0]["race_number"] == 1


def test_parse_race(adapter, attheraces_race_html):
    race_details = {
        "course": "Fontwell",
        "time": "14:12",
        "name": "Southern Cranes And Access Conditional Jockeys' Handicap Hurdle",
        "url": "https://www.attheraces.com/racecard/Fontwell/07-September-2025/1412",
        "race_number": 1,
    }
    race = adapter._parse_race(attheraces_race_html, race_details)
    assert isinstance(race, NormalizedRace)
    assert race.track_name == "Fontwell"
    assert race.race_type == "Southern Cranes And Access Conditional Jockeys' Handicap Hurdle"
    assert len(race.runners) == 2
    assert isinstance(race.runners[0], NormalizedRunner)
    assert race.runners[0].name == "Youremyeverything"
    assert race.runners[0].odds == 7.0
    assert race.runners[1].name == "Speedy Smartie"
    assert race.runners[1].odds == 3.5


@pytest.mark.anyio
async def test_fetch(adapter, attheraces_racecards_html, attheraces_race_html):
    with patch("paddock_parser.adapters.attheraces_adapter.get_page_content") as mock_get_page_content:

        async def mock_return(url):
            if "racecards" in url:
                return attheraces_racecards_html
            return attheraces_race_html

        mock_get_page_content.side_effect = mock_return

        races = await adapter.fetch()

        assert len(races) == 1
        race = races[0]
        assert isinstance(race, NormalizedRace)
        assert race.track_name == "Fontwell"
        assert "Southern Cranes" in race.race_type
        assert len(race.runners) == 2
        assert isinstance(race.runners[0], NormalizedRunner)
        assert race.runners[0].name == "Youremyeverything"
        assert race.runners[0].odds == 7.0
        assert race.runners[1].name == "Speedy Smartie"
        assert race.runners[1].odds == 3.5
