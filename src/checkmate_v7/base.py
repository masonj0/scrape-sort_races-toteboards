"""
Checkmate V7: `base.py` - Core abstractions and base classes.
"""
import logging
import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import List

import aiohttp

# Moved from services.py to break circular dependency
from .models import Race


class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    async def __aenter__(self):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.last_failure_time = time.time()
        elif self.state == "half-open":
            self.failure_count = 0
            self.state = "closed"


class DefensiveFetcher:
    def __init__(self):
        self.circuit_breakers = {}

    async def fetch(self, url, headers=None, response_type='text'):
        return await self._request('GET', url, headers=headers, response_type=response_type)

    async def post(self, url, headers=None, json_data=None, response_type='json'):
        return await self._request('POST', url, headers=headers, json_data=json_data, response_type=response_type)

    async def _request(self, method, url, headers=None, json_data=None, response_type='text'):
        domain = url.split('/')[2]
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = CircuitBreaker()

        cb = self.circuit_breakers[domain]

        retries = 5
        for i in range(retries):
            try:
                async with cb:
                    async with aiohttp.ClientSession(headers=headers) as session:
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                        async with session.request(method, url, json=json_data, timeout=15) as response:
                            response.raise_for_status()
                            if response_type == 'json':
                                return await response.json()
                            else:
                                return await response.text()
            except Exception as e:
                logging.warning(f"Attempt {i+1}/{retries} failed for {method} {url}: {e}")
                if i < retries - 1:
                    wait_time = (2 ** i) + random.uniform(0, 1)
                    logging.info(f"Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"All retries failed for {method} {url}")
                    raise


class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher

    @abstractmethod
    async def fetch_races(self) -> List[Race]:
        raise NotImplementedError
