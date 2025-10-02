# python_service/adapters/pointsbet_adapter.py

from typing import Dict, Any
from .base import BaseAdapter

class PointsBetAdapter(BaseAdapter):
    """
    A stub adapter for PointsBet data. To be implemented.
    """
    SOURCE_ID = "pointsbet"

    async def fetch_races(self) -> Dict[str, Any]:
        """
        Asynchronously fetches race data from PointsBet.
        This is a stub and returns an empty list.
        """
        self.logger.warning(f"Adapter '{self.SOURCE_ID}' is a stub and returns no data.")
        # The new engine expects a dictionary with a "races" key.
        return {"races": []}