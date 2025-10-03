# python_service/adapters/base.py

import logging
import aiohttp
from typing import Optional, Dict, Any

class BaseAdapter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch_races(self) -> Dict[str, Any]:
        raise NotImplementedError