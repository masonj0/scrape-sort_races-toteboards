# python_service/adapters/base_v3.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, List

from ..models import Race
from .base import BaseAdapter # Inherit to retain retry logic, logging, etc.

class BaseAdapterV3(BaseAdapter, ABC):
    """
    An architecturally superior abstract base class for data adapters.

    This class enforces a rigid, standardized implementation pattern by requiring all
    subclasses to implement their own `_fetch_data` and `_parse_races` methods.
    This separates the concerns of data retrieval from data parsing, leading to
    cleaner, more maintainable, and more consistent adapter code.
    """

    @abstractmethod
    async def _fetch_data(self, date: str) -> Any:
        """
        Fetches the raw data (e.g., HTML, JSON) for the given date.
        This is the only method that should interact with the network.
        """
        raise NotImplementedError

    @abstractmethod
    def _parse_races(self, raw_data: Any) -> List[Race]:
        """
        Parses the raw data fetched by _fetch_data into a list of Race objects.
        This method should be pure and contain no network logic.
        """
        raise NotImplementedError

    async def fetch_races(self, date: str) -> List[Race]:
        """
        The public-facing method to get races. Orchestrates the fetch and parse process.
        Subclasses should NOT override this method.
        """
        races = []
        try:
            raw_data = await self._fetch_data(date)
            if raw_data is None:
                self.logger.warning(f"Fetching data for {self.SOURCE_NAME} on {date} returned None.")
                return []

            parsed_races = self._parse_races(raw_data)
            for race in parsed_races:
                races.append(race)

        except Exception:
            self.logger.error(
                f"An unexpected error occurred in the get_races pipeline for {self.SOURCE_NAME}.",
                exc_info=True
            )
        return races