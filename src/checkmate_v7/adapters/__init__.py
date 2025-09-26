# src/checkmate_v7/adapters/__init__.py

from .AndWereOff import SkySportsAdapter, AtTheRacesAdapter, BetfairDataScientistAdapter, FanDuelApiAdapter, TVGAdapter
from .Stablemates import EquibaseAdapter, RacingAndSportsAdapter

PRODUCTION_ADAPTERS = [SkySportsAdapter, AtTheRacesAdapter, BetfairDataScientistAdapter, FanDuelApiAdapter, TVGAdapter]
DEVELOPMENT_ADAPTERS = [EquibaseAdapter, RacingAndSportsAdapter]

__all__ = ['PRODUCTION_ADAPTERS', 'DEVELOPMENT_ADAPTERS']