# python_service/adapters/__init__.py

from .tvg_adapter import TVGAdapter
from .betfair_adapter import BetfairAdapter
from .pointsbet_adapter import PointsBetAdapter
from .racing_and_sports_adapter import RacingAndSportsAdapter

# Define the public API for the adapters package, making it easy for the
# orchestrator to discover and use them.
__all__ = [
    "TVGAdapter",
    "BetfairAdapter",
    "PointsBetAdapter",
    "RacingAndSportsAdapter",
]