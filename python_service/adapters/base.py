# python_service/adapters/base.py

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import httpx

class BaseAdapter(ABC):
    def __init__(self, source_name: str, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        raise NotImplementedError

    async def make_request(self, http_client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                full_url = f"{self.base_url}{url}"
                self.logger.info(f"Requesting {method} {full_url}")
                response = await http_client.request(method, full_url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self.logger.warning(f"Request failed for {self.source_name} (attempt {retry_count + 1}/{self.max_retries}): {e}")
                retry_count += 1
                if retry_count >= self.max_retries:
                    self.logger.error(f"Max retries exceeded for {self.source_name}. Aborting.")
                    raise
                backoff = 1 * (2 ** retry_count) # Exponential backoff
                await asyncio.sleep(backoff)
        raise Exception("make_request failed after max retries")

    def get_status(self) -> Dict[str, Any]:
        """Returns a dictionary representing the adapter's default status."""
        return {"adapter_name": self.source_name, "status": "OK"}
