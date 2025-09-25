# src/checkmate_v7/adapters/__init__.py
from .AndWereOff import SkySportsAdapter, AtTheRacesAdapter, FanDuelApiAdapter, BetfairDataScientistAdapter
from .Stablemates import EquibaseAdapter

PRODUCTION_ADAPTERS = [SkySportsAdapter, AtTheRacesAdapter, FanDuelApiAdapter, BetfairDataScientistAdapter]
DEVELOPMENT_ADAPTERS = [EquibaseAdapter]

__all__ = ['PRODUCTION_ADAPTERS', 'DEVELOPMENT_ADAPTERS']