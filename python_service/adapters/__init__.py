# python_service/adapters/__init__.py

from .tvg_adapter import TVGAdapter
from .betfair_adapter import BetfairExchangeAdapter
from .pointsbet_adapter import PointsBetAdapter

# Define the public API for the adapters package, making it easy for the
# orchestrator to discover and use them.
__all__ = [
    "TVGAdapter",
    "BetfairExchangeAdapter",
    "PointsBetAdapter",
]