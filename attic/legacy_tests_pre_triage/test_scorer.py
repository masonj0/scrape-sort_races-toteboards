import pytest
from unittest.mock import patch
from src.paddock_parser.models import Race, Runner
from src.paddock_parser.scorer import RaceScorer, score_races

@pytest.fixture
def sample_weights():
    """Fixture for sample scorer weights."""
    return {
        "FIELD_SIZE_WEIGHT": 0.5,
        "FAVORITE_ODDS_WEIGHT": 0.3,
        "CONTENTION_WEIGHT": 0.2,
    }

@pytest.fixture
def race_with_clear_favorite():
    """Fixture for a race with a clear favorite and low contention."""
    return Race(
        race_id="R1", venue="Test", race_time="14:00", source="Test", race_number=1, is_handicap=False, number_of_runners=8,
        runners=[
            Runner(name="Favorite", odds=2.0),
            Runner(name="Runner2", odds=8.0),
        ]
    )

@pytest.fixture
def race_with_high_contention():
    """Fixture for a race with high contention (two joint favorites)."""
    return Race(
        race_id="R2", venue="Test", race_time="15:00", source="Test", race_number=2, is_handicap=True, number_of_runners=10,
        runners=[
            Runner(name="JointFav1", odds=4.5),
            Runner(name="JointFav2", odds=4.5),
        ]
    )

def test_race_scorer_initialization(sample_weights):
    scorer = RaceScorer(weights=sample_weights)
    assert scorer.weights == sample_weights

@patch('src.paddock_parser.scorer.SCORER_WEIGHTS', {"FIELD_SIZE_WEIGHT": 0.5, "FAVORITE_ODDS_WEIGHT": 0.3, "CONTENTION_WEIGHT": 0.2})
def test_race_scorer_initialization_from_config():
    scorer = RaceScorer()
    assert scorer.weights["FIELD_SIZE_WEIGHT"] == 0.5

def test_score_calculation_low_contention(sample_weights, race_with_clear_favorite):
    scorer = RaceScorer(weights=sample_weights)
    scores = scorer.score(race_with_clear_favorite)
    assert scores['field_size_score'] == pytest.approx(1/8)
    assert scores['favorite_odds_score'] == pytest.approx(2.0)
    assert scores['contention_score'] == pytest.approx(6.0)
    expected_score = (1/8 * 0.5) + (2.0 * 0.3) + (6.0 * 0.2)
    assert scores['total_score'] == pytest.approx(expected_score)

def test_score_calculation_high_contention(sample_weights, race_with_high_contention):
    scorer = RaceScorer(weights=sample_weights)
    scores = scorer.score(race_with_high_contention)
    assert scores['field_size_score'] == pytest.approx(1/10)
    assert scores['favorite_odds_score'] == pytest.approx(4.5)
    assert scores['contention_score'] == pytest.approx(0.0)
    expected_score = (0.1 * 0.5) + (4.5 * 0.3) + (0.0 * 0.2)
    assert scores['total_score'] == pytest.approx(expected_score)

@patch('src.paddock_parser.scorer.SCORER_WEIGHTS', {"FIELD_SIZE_WEIGHT": 0.5, "FAVORITE_ODDS_WEIGHT": 0.3, "CONTENTION_WEIGHT": 0.2})
def test_score_races_function(race_with_clear_favorite):
    races = [race_with_clear_favorite]
    scored_races = score_races(races)
    expected_score = (1/8 * 0.5) + (2.0 * 0.3) + (6.0 * 0.2)
    assert hasattr(scored_races[0], 'score')
    assert hasattr(scored_races[0], 'scores')
    assert scored_races[0].score == pytest.approx(expected_score)
    assert scored_races[0].scores['total_score'] == pytest.approx(expected_score)
