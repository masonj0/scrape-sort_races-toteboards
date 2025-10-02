# python_service/adapters/base.py

import abc
import logging
import aiohttp
from typing import Dict, Any

class BaseAdapter(abc.ABC):
    """
    An abstract base class for all data source adapters, enforcing a
    consistent asynchronous interface.
    """

    def __init__(self):
        """
        Initializes the adapter. Each adapter is responsible for managing
        its own resources, such as HTTP sessions.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Provides a lazy-initialized aiohttp.ClientSession."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    @abc.abstractmethod
    async def fetch_races(self) -> Dict[str, Any]:
        """
        Abstract method to fetch race data from the source asynchronously.

        This method must be implemented by all subclasses. It should return
        a dictionary containing race data or error information.
        A consistent format is expected, e.g., {"races": [...], "error": "..."}
        """
        raise NotImplementedError("Each adapter must implement the async fetch_races method.")

    async def close(self):
        """
        Closes the underlying aiohttp session, if it was created.
        This is crucial for graceful shutdown.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self.logger.info(f"Closed session for {self.__class__.__name__}")