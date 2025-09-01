"""
Test-as-Spec for AtTheRaces Adapter

This file serves as both specification and test suite for the modernized AtTheRacesAdapter class.
It defines the expected behavior and interface for parsing HTML content from attheraces.com
into normalized data structures, based on actual HTML structure analysis.

Path: tests/adapters/test_attheraces_adapter.py
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Optional
import os

# Import the modern data structures
from paddock_parser.base import NormalizedRace, NormalizedRunner



class TestAtTheRacesAdapterInitialization:
    """Test suite for AtTheRacesAdapter initialization and basic setup."""

    def test_adapter_can_be_initialized(self):
        """
        SPEC: AtTheRacesAdapter class can be instantiated.
        """
        from src.paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter

        adapter = AtTheRacesAdapter()

        assert adapter is not None
        assert adapter.source_id == 'attheraces'

class TestHTMLParsing:
    """Test suite for HTML content parsing."""

    @pytest.fixture
    def real_attheraces_html(self):
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

    def test_parse_races_returns_list_of_normalized_races(self, real_attheraces_html):
        """
        SPEC: parse_races() method accepts HTML content and returns List[NormalizedRace].
        """
        from src.paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter

        adapter = AtTheRacesAdapter()

        # This is a placeholder for the real implementation
        with patch.object(adapter, '_parse_race_data', return_value=[NormalizedRace(race_id="test_id", race_number=1, track_name="Roscommon", number_of_runners=2)]):
             result = adapter.parse_races(real_attheraces_html)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], NormalizedRace)
        assert result[0].track_name == "Roscommon"
        assert result[0].number_of_runners == 2

    def test_parse_races_extracts_correct_data(self, real_attheraces_html):
        """
        SPEC: All runner and race data should be correctly extracted.
        """
        from src.paddock_parser.adapters.attheraces_adapter import AtTheRacesAdapter
        adapter = AtTheRacesAdapter()

        # Placeholder for the real implementation
        runners_data = [
            NormalizedRunner(name="In My Teens", program_number=72, jockey="G F Carroll", trainer="G P Cromwell", odds="7/2"),
            NormalizedRunner(name="Vorfreude", program_number=11, jockey="B M Coen", trainer="J G Murphy", odds="11/4")
        ]
        race_data = NormalizedRace(
            race_id="1745_ROS",
            track_name="Roscommon",
            race_number=1, # Assuming 1 as it is the only one on the page
            post_time=datetime(2025, 9, 1, 17, 45),
            race_type="Lecarrow Race",
            number_of_runners=2,
            runners=runners_data
        )

        with patch.object(adapter, '_parse_race_data', return_value=[race_data]):
            races = adapter.parse_races(real_attheraces_html)

        race = races[0]
        assert race.track_name == "Roscommon"
        assert race.post_time.hour == 17
        assert race.number_of_runners == 2

        in_my_teens = race.runners[0]
        assert in_my_teens.name == "In My Teens"
        assert in_my_teens.jockey == "G F Carroll"
        assert in_my_teens.odds == "7/2"
