from typing import Optional

from .base import NormalizedRace


class RaceScorer:
    """
    Analyzes a NormalizedRace to produce a score based on specific criteria.
    """

    def score(self, race: NormalizedRace) -> float:
        """
        Calculates a score for a single normalized race based on the number of runners.
        The logic is adapted from the legacy V2Scorer's field size scoring.
        """
        if not race.number_of_runners:
            return 0.0

        field_size = race.number_of_runners

        if 5 <= field_size <= 7:
            return 100.0
        if 8 <= field_size <= 10:
            return 80.0
        if 3 <= field_size <= 4:
            return 60.0
        if 11 <= field_size <= 12:
            return 40.0

        return 20.0
