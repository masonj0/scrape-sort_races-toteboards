from paddock_parser.scorer import RaceScorer
from paddock_parser.base import NormalizedRace, NormalizedRunner

def test_race_scorer():
    """
    Tests the RaceScorer logic.
    It should give higher scores to races with fewer runners.
    """
    # 1. Setup
    scorer = RaceScorer()

    # Create mock races with different numbers of runners
    # Note: We only need to populate the number_of_runners field for this test
    small_race = NormalizedRace(
        race_id="test-1",
        track_name="Test Track",
        race_number=1,
        number_of_runners=6, # Optimal range 5-7
    )

    medium_race = NormalizedRace(
        race_id="test-2",
        track_name="Test Track",
        race_number=2,
        number_of_runners=9, # Good range 8-10
    )

    large_race = NormalizedRace(
        race_id="test-3",
        track_name="Test Track",
        race_number=3,
        number_of_runners=15, # Low score range
    )

    # 2. Execution
    score_small = scorer.score(small_race)
    score_medium = scorer.score(medium_race)
    score_large = scorer.score(large_race)

    # 3. Assertions

    # Assert specific scores based on the adapted logic
    assert score_small == 100.0
    assert score_medium == 80.0
    assert score_large == 20.0

    # Assert the relationship between the scores
    assert score_small > score_medium
    assert score_medium > score_large
