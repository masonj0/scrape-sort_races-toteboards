#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Base Adapter (v2 - Hardened with Tenacity)
# ==============================================================================

import asyncio
import httpx
import structlog
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

log = structlog.get_logger(__name__)

class BaseAdapter(ABC):
    """The resilient base class for all data source adapters."""

    def __init__(self, source_name: str, base_url: str, timeout: int = 20, max_retries: int = 3):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        raise NotImplementedError

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True # Reraise the last exception after retries are exhausted
    )
    async def make_request(self, http_client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
        """Makes a resilient HTTP request with automatic retries and exponential backoff."""
        try:
            full_url = url if url.startswith('http') else f"{self.base_url}{url}"
            log.info(f"Requesting...", adapter=self.source_name, method=method, url=full_url)
            response = await http_client.request(method, full_url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            log.warning("Request failed, tenacity will retry...", adapter=self.source_name, error=str(e))
            raise # Reraise to trigger tenacity's retry mechanism
        except httpx.HTTPStatusError as e:
            log.warning("HTTP status error, tenacity will retry...", adapter=self.source_name, status_code=e.response.status_code, error=str(e))
            raise # Reraise to trigger tenacity's retry mechanism

    def get_status(self) -> Dict[str, Any]:
        return {"adapter_name": self.source_name, "status": "OK"}