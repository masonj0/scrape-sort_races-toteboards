# python_service/adapters/base.py

import httpx
import structlog
from abc import ABC, abstractmethod
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError, AsyncRetrying

log = structlog.get_logger(__name__)

class BaseAdapter(ABC):
    def __init__(self, source_name: str, base_url: str, timeout: int = 20, max_retries: int = 3):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        raise NotImplementedError

    async def make_request(self, http_client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
        retryer = AsyncRetrying(stop=stop_after_attempt(self.max_retries), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
        try:
            async for attempt in retryer:
                with attempt:
                    full_url = url if url.startswith('http') else f"{self.base_url}{url}"
                    response = await http_client.request(method, full_url, timeout=self.timeout, **kwargs)
                    response.raise_for_status()
                    try:
                        return response.json()
                    except Exception:
                        return response.text
        except RetryError as e:
            log.error(f"Max retries exceeded for {self.source_name}", final_error=str(e))
            return None

    def get_status(self) -> Dict[str, Any]:
        return {"adapter_name": self.source_name, "status": "OK"}