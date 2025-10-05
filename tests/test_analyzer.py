import pytest
from decimal import Decimal
from datetime import datetime
from python_service.models import Race, Runner, OddsData
from python_service.analyzer import TrifectaAnalyzer

@pytest.fixture
def sample_races():
    """Provides a list of sample Race objects for testing."""
    return [
        # Race 1: Qualifies (8 runners, fav odds > 2.0)
        Race(
            id="test_race_1",
            venue="Test Park",
            race_number=1,
            start_time=datetime.now(),
            source="Test",
            runners=[
                Runner(number=i, name=f"Runner {i}", odds={
                    "TestOdds": OddsData(win=Decimal(str(2.5 + i)), source="TestOdds", last_updated=datetime.now())
                }) for i in range(1, 9)
            ]
        ),
        # Race 2: Fails (not enough runners)
        Race(
            id="test_race_2",
            venue="Test Park",
            race_number=2,
            start_time=datetime.now(),
            source="Test",
            runners=[
                Runner(number=i, name=f"Runner {i}", odds={}) for i in range(1, 5)
            ]
        ),
        # Race 3: Fails (favorite odds too low)
        Race(
            id="test_race_3",
            venue="Test Park",
            race_number=3,
            start_time=datetime.now(),
            source="Test",
            runners=[
                Runner(number=i, name=f"Runner {i}", odds={
                    "TestOdds": OddsData(win=Decimal(str(1.5 + i)), source="TestOdds", last_updated=datetime.now())
                }) for i in range(1, 9)
            ]
        ),
        # Race 4: Qualifies (10 runners, fav odds > 2.0)
        Race(
            id="test_race_4",
            venue="Test Park",
            race_number=4,
            start_time=datetime.now(),
            source="Test",
            runners=[
                Runner(number=i, name=f"Runner {i}", odds={
                    "TestOdds": OddsData(win=Decimal(str(3.0 + i)), source="TestOdds", last_updated=datetime.now())
                }) for i in range(1, 11)
            ]
        ),
        # Race 5: Fails (scratched runners bring it below threshold)
        Race(
            id="test_race_5",
            venue="Test Park",
            race_number=5,
            start_time=datetime.now(),
            source="Test",
            runners=[
                Runner(number=1, name="Runner 1", odds={}, scratched=True),
                Runner(number=2, name="Runner 2", odds={}, scratched=True),
                Runner(number=3, name="Runner 3", odds={}, scratched=True),
                Runner(number=4, name="Runner 4", odds={}),
                Runner(number=5, name="Runner 5", odds={}),
                Runner(number=6, name="Runner 6", odds={}),
                Runner(number=7, name="Runner 7", odds={}),
                Runner(number=8, name="Runner 8", odds={}),
            ]
        ),
    ]

def test_qualify_races_success(sample_races):
    """
    Tests that the analyzer correctly identifies races that meet the
    qualification criteria.
    """
    analyzer = TrifectaAnalyzer(min_runners=8, min_favorite_odds=2.0)
    qualified_races = analyzer.qualify_races(sample_races)

    qualified_ids = {race.id for race in qualified_races}

    assert "test_race_1" in qualified_ids
    assert "test_race_4" in qualified_ids
    assert len(qualified_races) == 2

def test_qualify_races_filters_correctly(sample_races):
    """
    Tests that the analyzer correctly filters out races that do not meet
    the qualification criteria.
    """
    analyzer = TrifectaAnalyzer(min_runners=8, min_favorite_odds=2.0)
    qualified_races = analyzer.qualify_races(sample_races)

    qualified_ids = {race.id for race in qualified_races}

    assert "test_race_2" not in qualified_ids  # Not enough runners
    assert "test_race_3" not in qualified_ids  # Favorite odds too low
    assert "test_race_5" not in qualified_ids  # Scratched runners
    assert len(qualified_races) == 2