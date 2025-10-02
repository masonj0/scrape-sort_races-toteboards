# python_service/adapters/betfair_adapter.py

from typing import Dict, Any
from .base import BaseAdapter

class BetfairAdapter(BaseAdapter):
    """
    A stub adapter for Betfair data. To be implemented.
    """
    SOURCE_ID = "betfair"

    async def fetch_races(self) -> Dict[str, Any]:
        """
        Asynchronously fetches race data from Betfair.
        This is a stub and returns an empty list.
        """
        self.logger.warning(f"Adapter '{self.SOURCE_ID}' is a stub and returns no data.")
        # The new engine expects a dictionary with a "races" key.
        return {"races": []}