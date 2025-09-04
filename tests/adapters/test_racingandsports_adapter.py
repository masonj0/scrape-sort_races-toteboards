import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from paddock_parser.base import NormalizedRace
from paddock_parser.adapters.racingandsports_adapter import RacingAndSportsAdapter

@pytest.fixture
def sample_json_data():
    """Loads the sample JSON data from the fixture file."""
    fixture_path = Path(__file__).parent / "racingandsports_sample.json"
    with open(fixture_path, 'r') as f:
        return f.read()

def test_parse_meetings_extracts_correct_information(sample_json_data):
    """
    Tests that the adapter can correctly parse the meeting-level JSON
    and extract the course names and form guide URLs.
    """
    adapter = RacingAndSportsAdapter()
    meetings = adapter.parse_meetings(sample_json_data)

    assert len(meetings) > 0

    # Check for a specific, known meeting in the results
    canberra_meeting = next((m for m in meetings if m['course'] == 'Canberra'), None)

    assert canberra_meeting is not None
    assert canberra_meeting['course'] == 'Canberra'
    assert "canberra" in canberra_meeting['url']
    assert "2025-09-05" in canberra_meeting['url']

    # Check another one for good measure
    haydock_meeting = next((m for m in meetings if m['course'] == 'Haydock Park'), None)
    assert haydock_meeting is not None
    assert haydock_meeting['course'] == 'Haydock Park'
    assert "haydock-park" in haydock_meeting['url']
