# python_service/adapters/base_v3.py
import time
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, List

import structlog

from ..models import Race
from .base import BaseAdapter # Inherit to retain retry logic, logging, circuit breaker state, etc.

class BaseAdapterV3(ABC):
    """
    An architecturally superior abstract base class for data adapters.

    This class enforces a rigid, standardized implementation pattern by requiring all
    subclasses to implement their own `_fetch_data` and `_parse_races` methods.
    It also includes a built-in circuit breaker to enhance resilience.
    """
    def __init__(self, source_name: str, base_url: str, timeout: int = 20, max_retries: int = 3):
        self.source_name = source_name
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = structlog.get_logger(adapter_name=source_name)
        # Circuit Breaker State
        self.circuit_breaker_tripped = False
        self.circuit_breaker_failure_count = 0
        self.circuit_breaker_last_failure = 0
        self.FAILURE_THRESHOLD = 3
        self.COOLDOWN_PERIOD_SECONDS = 300  # 5 minutes

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

    async def get_races(self, date: str) -> AsyncGenerator[Race, None]:
        """
        The public-facing method to get races. Orchestrates the fetch and parse process.
        Includes a circuit breaker to prevent repeated calls to a failing adapter.
        Subclasses should NOT override this method.
        """
        # Check Circuit Breaker state
        if self.circuit_breaker_tripped:
            if time.time() - self.circuit_breaker_last_failure < self.COOLDOWN_PERIOD_SECONDS:
                self.logger.warning(f"Circuit breaker for {self.SOURCE_NAME} is tripped. Skipping fetch.")
                return
            else:
                self.logger.info(f"Cooldown period for {self.SOURCE_NAME} has passed. Resetting circuit breaker.")
                self.circuit_breaker_failure_count = 0
                self.circuit_breaker_tripped = False

        try:
            raw_data = await self._fetch_data(date)
            if raw_data is None:
                self.logger.warning(f"Fetching data for {self.SOURCE_NAME} on {date} returned None.")
                return

            parsed_races = self._parse_races(raw_data)
            for race in parsed_races:
                yield race

            # Reset failure count on success
            self.circuit_breaker_failure_count = 0

        except Exception:
            self.logger.error(
                f"An unexpected error occurred in the get_races pipeline for {self.SOURCE_NAME}.",
                exc_info=True
            )
            # Handle circuit breaker logic on failure
            self.circuit_breaker_failure_count += 1
            self.circuit_breaker_last_failure = time.time()
            if self.circuit_breaker_failure_count >= self.FAILURE_THRESHOLD:
                self.circuit_breaker_tripped = True
                self.logger.critical(f"Circuit breaker for {self.SOURCE_NAME} has been tripped after {self.FAILURE_THRESHOLD} failures.")
            return
