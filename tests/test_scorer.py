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
            Runner(name="Runner3", odds=10.0),
            Runner(name="Runner4", odds=15.0),
            Runner(name="Runner5", odds=20.0),
            Runner(name="Runner6", odds=25.0),
            Runner(name="Runner7", odds=30.0),
            Runner(name="Runner8", odds=50.0),
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
            Runner(name="Runner3", odds=5.0),
            Runner(name="Runner4", odds=8.0),
            Runner(name="Runner5", odds=12.0),
            Runner(name="Runner6", odds=12.0),
            Runner(name="Runner7", odds=16.0),
            Runner(name="Runner8", odds=20.0),
            Runner(name="Runner9", odds=25.0),
            Runner(name="Runner10", odds=33.0),
        ]
    )

def test_race_scorer_initialization(sample_weights):
    """
    SPEC: The RaceScorer must initialize with the provided weights.
    """
    scorer = RaceScorer(weights=sample_weights)
    assert scorer.weights == sample_weights

@patch('src.paddock_parser.scorer.SCORER_WEIGHTS', {
    "FIELD_SIZE_WEIGHT": 0.5,
    "FAVORITE_ODDS_WEIGHT": 0.3,
    "CONTENTION_WEIGHT": 0.2,
})
def test_race_scorer_initialization_from_config():
    """
    SPEC: The RaceScorer must initialize with weights from the config if none are provided.
    """
    scorer = RaceScorer()
    assert scorer.weights["FIELD_SIZE_WEIGHT"] == 0.5
    assert scorer.weights["FAVORITE_ODDS_WEIGHT"] == 0.3
    assert scorer.weights["CONTENTION_WEIGHT"] == 0.2

def test_score_calculation_low_contention(sample_weights, race_with_clear_favorite):
    """
    SPEC: The final score must be the weighted sum of the individual factor scores.
    """
    scorer = RaceScorer(weights=sample_weights)
    scores = scorer.score(race_with_clear_favorite)

    # Raw scores
    assert scores['field_size_score'] == pytest.approx(1/8)
    assert scores['favorite_odds_score'] == pytest.approx(2.0)
    assert scores['contention_score'] == pytest.approx(8.0 - 2.0)

    # Expected total score
    # weighted_field = (1/8) * 0.5 = 0.0625
    # weighted_odds = 2.0 * 0.3 = 0.6
    # weighted_contention = (8.0 - 2.0) * 0.2 = 1.2
    # total_score = 0.0625 + 0.6 + 1.2 = 1.8625
    expected_score = (1/8 * 0.5) + (2.0 * 0.3) + (6.0 * 0.2)
    assert scores['total_score'] == pytest.approx(expected_score)

def test_score_calculation_high_contention(sample_weights, race_with_high_contention):
    """
    SPEC: The final score must correctly reflect a high contention scenario.
    """
    scorer = RaceScorer(weights=sample_weights)
    scores = scorer.score(race_with_high_contention)

    # Raw scores
    assert scores['field_size_score'] == pytest.approx(1/10)
    assert scores['favorite_odds_score'] == pytest.approx(4.5)
    assert scores['contention_score'] == pytest.approx(4.5 - 4.5)

    # Expected total score
    # weighted_field = (1/10) * 0.5 = 0.05
    # weighted_odds = 4.5 * 0.3 = 1.35
    # weighted_contention = 0.0 * 0.2 = 0.0
    # total_score = 0.05 + 1.35 + 0.0 = 1.40
    expected_score = (0.1 * 0.5) + (4.5 * 0.3) + (0.0 * 0.2)
    assert scores['total_score'] == pytest.approx(expected_score)

def test_score_handles_no_runners(sample_weights):
    """
    SPEC: If a race has no runners, the total score should be 0 to avoid errors.
    """
    scorer = RaceScorer(weights=sample_weights)
    race = Race(
        race_id="R3", venue="Empty", race_time="16:00", source="Test", race_number=3, is_handicap=False, number_of_runners=0,
        runners=[]
    )
    scores = scorer.score(race)
    assert scores['total_score'] == 0
    assert scores['field_size_score'] == 0
    assert scores['favorite_odds_score'] == 0
    assert scores['contention_score'] == 0

def test_score_handles_one_runner(sample_weights):
    """
    SPEC: If a race has only one runner, contention score should be handled gracefully.
    The contention score should be the favorite's odds.
    """
    scorer = RaceScorer(weights=sample_weights)
    race = Race(
        race_id="R4", venue="Walkover", race_time="17:00", source="Test", race_number=4, is_handicap=False, number_of_runners=1,
        runners=[Runner(name="Solo", odds=1.5)]
    )
    scores = scorer.score(race)

    # Raw scores
    assert scores['field_size_score'] == pytest.approx(1.0)
    assert scores['favorite_odds_score'] == pytest.approx(1.5)
    assert scores['contention_score'] == pytest.approx(1.5) # As per spec for single runner

    # Expected total score
    # weighted_field = 1.0 * 0.5 = 0.5
    # weighted_odds = 1.5 * 0.3 = 0.45
    # weighted_contention = 1.5 * 0.2 = 0.30
    # total_score = 0.5 + 0.45 + 0.30 = 1.25
    expected_score = (1.0 * 0.5) + (1.5 * 0.3) + (1.5 * 0.2)
    assert scores['total_score'] == pytest.approx(expected_score)

@patch('src.paddock_parser.scorer.SCORER_WEIGHTS', {
    "FIELD_SIZE_WEIGHT": 0.5,
    "FAVORITE_ODDS_WEIGHT": 0.3,
    "CONTENTION_WEIGHT": 0.2,
})
def test_score_races_function(race_with_clear_favorite, race_with_high_contention):
    """
    SPEC: The score_races function should correctly score and attach results to a list of races.
    """
    races = [race_with_clear_favorite, race_with_high_contention]
    scored_races = score_races(races)

    # Check race 1
    expected_score_1 = (1/8 * 0.5) + (2.0 * 0.3) + (6.0 * 0.2)
    assert hasattr(scored_races[0], 'score')
    assert hasattr(scored_races[0], 'scores')
    assert scored_races[0].score == pytest.approx(expected_score_1)
    assert scored_races[0].scores['total_score'] == pytest.approx(expected_score_1)

    # Check race 2
    expected_score_2 = (0.1 * 0.5) + (4.5 * 0.3) + (0.0 * 0.2)
    assert hasattr(scored_races[1], 'score')
    assert hasattr(scored_races[1], 'scores')
    assert scored_races[1].score == pytest.approx(expected_score_2)
    assert scored_races[1].scores['total_score'] == pytest.approx(expected_score_2)
