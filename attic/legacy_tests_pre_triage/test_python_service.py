#!/usr/bin/env python3
# ==============================================================================
# == Checkmate V8 - Python Service Unit Tests
# ==============================================================================
# Establishes the foundational test suite for the Python Collection Corps.
# ==============================================================================

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path to import from python_service
sys.path.insert(0, str(Path(__file__).parent.parent / "python_service"))

from engine import TrifectaAnalyzer, Settings, Race, Runner

@pytest.fixture
def analyzer():
    """Provides a fresh TrifectaAnalyzer for each test."""
    return TrifectaAnalyzer()

@pytest.fixture
def settings():
    """Provides a standard Settings object."""
    return Settings()

def test_perfect_race_is_qualified(analyzer, settings):
    """Tests that a race meeting all ideal criteria is qualified with a high score."""
    perfect_race = Race(
        race_id='test_perfect_1',
        track_name='Ideal Park',
        runners=[
            Runner(name='Fav', odds=2.5),
            Runner(name='Second', odds=5.0),
            Runner(name='Third', odds=10.0),
            Runner(name='Fourth', odds=12.0),
            Runner(name='Fifth', odds=15.0),
            Runner(name='Sixth', odds=20.0)
        ]
    )
    result = analyzer.analyze_race(perfect_race, settings)
    assert result.is_qualified is True
    assert result.checkmate_score == 100.0

def test_small_field_is_not_qualified(analyzer, settings):
    """Tests that a race with too few runners fails qualification."""
    small_field_race = Race(
        race_id='test_small_field_1',
        track_name='Small Downs',
        runners=[
            Runner(name='A', odds=3.0),
            Runner(name='B', odds=4.0),
            Runner(name='C', odds=5.0)
        ]
    )
    result = analyzer.analyze_race(small_field_race, settings)
    assert result.is_qualified is False
    assert result.checkmate_score < settings.QUALIFICATION_SCORE

def test_weak_favorite_is_not_qualified(analyzer, settings):
    """Tests that a race with a high-odds favorite fails qualification."""
    weak_fav_race = Race(
        race_id='test_weak_fav_1',
        track_name='Longshot Lane',
        runners=[
            Runner(name='WeakFav', odds=4.0), # Odds are > MAX_FAV_ODDS
            Runner(name='B', odds=5.0),
            Runner(name='C', odds=6.0),
            Runner(name='D', odds=7.0),
            Runner(name='E', odds=8.0)
        ]
    )
    result = analyzer.analyze_race(weak_fav_race, settings)
    assert result.is_qualified is False