# python_service/adapters/__init__.py

from .tvg_adapter import TVGAdapter
from .betfair_adapter import BetfairAdapter
from .betfair_greyhound_adapter import BetfairGreyhoundAdapter
from .at_the_races_adapter import AtTheRacesAdapter
from .racing_and_sports_adapter import RacingAndSportsAdapter
from .harness_adapter import HarnessAdapter
from .greyhound_adapter import GreyhoundAdapter
from .racing_and_sports_greyhound_adapter import RacingAndSportsGreyhoundAdapter
from .pointsbet_greyhound_adapter import PointsBetGreyhoundAdapter

# Define the public API for the adapters package, making it easy for the
# orchestrator to discover and use them.
__all__ = [
    "TVGAdapter",
    "BetfairAdapter",
    "BetfairGreyhoundAdapter",
    "RacingAndSportsGreyhoundAdapter",
    "AtTheRacesAdapter",
    "PointsBetGreyhoundAdapter",
    "RacingAndSportsAdapter",
    "HarnessAdapter",
    "GreyhoundAdapter",
]