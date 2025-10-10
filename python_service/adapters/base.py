#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Base Adapter (v2 - Hardened with Tenacity)
# ==============================================================================

import httpx
import structlog
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError, AsyncRetrying

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

    async def make_request(self, http_client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Optional[Any]:
        """Makes a resilient HTTP request with automatic retries using Tenacity."""
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True
        )
        try:
            async for attempt in retryer:
                with attempt:
                    try:
                        full_url = url if url.startswith('http') else f"{self.base_url}{url}"
                        log.info(f"Requesting...", adapter=self.source_name, method=method, url=full_url, attempt=attempt.retry_state.attempt_number)
                        response = await http_client.request(method, full_url, timeout=self.timeout, **kwargs)
                        response.raise_for_status()
                        return response.json()
                    except (httpx.RequestError, httpx.HTTPStatusError) as e:
                        log.warning("Request failed, tenacity will retry...", adapter=self.source_name, error=str(e))
                        raise # Reraise to trigger tenacity's retry mechanism
        except RetryError as e:
            log.error(f"Max retries exceeded for {self.source_name}. Aborting request.", final_error=str(e))
            return None # Return None on total failure

    def get_status(self) -> Dict[str, Any]:
        return {"adapter_name": self.source_name, "status": "OK"}

    def _format_response(self, races: List, start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        """Formats the adapter's response consistently."""
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }