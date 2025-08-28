from paddock_parser.adapters.base import NormalizedRace

class RaceScorer:
    """
    Calculates a score for a given race based on predefined criteria.
    """
    def score(self, race: NormalizedRace) -> float:
        """
        The current scoring algorithm is a simple placeholder.
        It returns the number of runners, rewarding larger fields.
        """
        if not isinstance(race, NormalizedRace) or race.number_of_runners is None:
            return 0.0

        return float(race.number_of_runners)
