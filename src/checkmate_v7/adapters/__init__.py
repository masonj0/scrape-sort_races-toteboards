# src/checkmate_v7/adapters/__init__.py

from .AndWereOff import SkySportsAdapter, AtTheRacesAdapter, BetfairDataScientistAdapter, FanDuelApiAdapter, TVGAdapter, BetfairExchangeAdapter
from .Stablemates import EquibaseAdapter, RacingAndSportsAdapter

PRODUCTION_ADAPTERS = [SkySportsAdapter, AtTheRacesAdapter, BetfairDataScientistAdapter, FanDuelApiAdapter, TVGAdapter, BetfairExchangeAdapter]
DEVELOPMENT_ADAPTERS = [EquibaseAdapter, RacingAndSportsAdapter]

__all__ = ['PRODUCTION_ADAPTERS', 'DEVELOPMENT_ADAPTERS']