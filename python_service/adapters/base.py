# python_service/adapters/base.py

import logging
from abc import ABC, abstractmethod
from typing import List
from ..models import RaceData

class BaseAdapter(ABC):
    """Abstract base class for all data adapters."""

    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def SOURCE_ID(self) -> str:
        """Unique identifier for the data source."""
        pass

    @abstractmethod
    def fetch_races(self) -> List[RaceData]:
        """Fetch and parse race data from the source."""
        pass