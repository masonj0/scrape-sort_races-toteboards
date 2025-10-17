# checkmate_service_v3.py
import asyncio
import json
import logging
import importlib
from datetime import datetime, timedelta

import aiohttp
import async_timeout

# --- Constants ---
ADAPTER_CONFIG = {
    "betfair": {"module": "betfair_adapter", "class": "BetfairAdapter"},
    "betfair_greyhound": {
        "module": "betfair_greyhound_adapter",
        "class": "BetfairGreyhoundAdapter",
    },
    "ladbrokes": {"module": "ladbrokes_adapter", "class": "LadbrokesAdapter"},
    "sportsbet": {"module": "sportsbet_adapter", "class": "SportsbetAdapter"},
    "pointsbet": {"module": "pointsbet_adapter", "class": "PointsbetAdapter"},
    "tab": {"module": "tab_adapter", "class": "TABAdapter"},
    "bluebet": {"module": "bluebet_adapter", "class": "BlueBetAdapter"},
    "unibet": {"module": "unibet_adapter", "class": "UnibetAdapter"},
    "palmerbet": {"module": "palmerbet_adapter", "class": "PalmerbetAdapter"},
}
CACHE_TTL_SECONDS = 300
CIRCUIT_BREAKER_THRESHOLD = 3
CIRCUIT_BREAKER_TIMEOUT_SECONDS = 60
LOG_LEVEL = logging.INFO
REQUEST_TIMEOUT_SECONDS = 10
OUTPUT_FILENAME = "races.json"

# --- Logging Configuration ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# --- In-memory Cache with TTL ---
class Cache:
    def __init__(self, ttl_seconds):
        self._cache = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key):
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() - entry["timestamp"] < self._ttl:
                logger.info(f"Cache hit for key: {key}")
                return entry["data"]
            else:
                logger.info(f"Cache expired for key: {key}")
        logger.info(f"Cache miss for key: {key}")
        return None

    def set(self, key, data):
        logger.info(f"Cache set for key: {key}")
        self._cache[key] = {"data": data, "timestamp": datetime.now()}


# --- Circuit Breaker ---
class CircuitBreaker:
    def __init__(self, threshold, timeout_seconds):
        self._threshold = threshold
        self._timeout = timedelta(seconds=timeout_seconds)
        self._failure_count = 0
        self._is_open = False
        self._last_failure_time = None

    @property
    def is_open(self):
        if self._is_open and self._last_failure_time:
            if datetime.now() - self._last_failure_time > self._timeout:
                self._reset()  # Half-open state
                logger.info("Circuit breaker transitioned to half-open state.")
        return self._is_open

    def record_failure(self):
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        if self._failure_count >= self._threshold:
            self._is_open = True
            logger.warning("Circuit breaker opened.")

    def record_success(self):
        self._reset()

    def _reset(self):
        self._failure_count = 0
        self._is_open = False
        self._last_failure_time = None
        logger.info("Circuit breaker has been reset.")


# --- Adapter Factory ---
def create_adapter(adapter_name):
    """Dynamically creates an adapter instance."""
    try:
        config = ADAPTER_CONFIG[adapter_name]
        module = importlib.import_module(f"adapters.{config['module']}")
        adapter_class = getattr(module, config["class"])
        return adapter_class()
    except (ImportError, KeyError, AttributeError) as e:
        logger.error(f"Failed to create adapter '{adapter_name}': {e}")
        return None


# --- Main Service Logic ---
class RaceService:
    def __init__(self, cache, circuit_breaker):
        self.cache = cache
        self.circuit_breaker = circuit_breaker
        self.adapters = {
            name: create_adapter(name) for name in ADAPTER_CONFIG if create_adapter(name)
        }

    async def fetch_from_adapter(self, session, adapter_name, adapter):
        """Fetches data from a single adapter with circuit breaker logic."""
        if self.circuit_breaker.is_open:
            logger.warning(
                f"Skipping {adapter_name} as circuit breaker is open."
            )
            return None

        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT_SECONDS):
                races = await adapter.get_races(session)
                self.circuit_breaker.record_success()
                return races
        except (aiohttp.ClientError, asyncio.TimeoutError, Exception) as e:
            logger.error(
                f"Error fetching data from {adapter_name}: {e}", exc_info=True
            )
            self.circuit_breaker.record_failure()
            return None

    async def get_all_races(self):
        """Gathers races from all configured adapters."""
        all_races = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for name, adapter in self.adapters.items():
                cached_races = self.cache.get(name)
                if cached_races:
                    all_races.extend(cached_races)
                else:
                    tasks.append(self.fetch_from_adapter(session, name, adapter))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                adapter_name = list(self.adapters.keys())[i]
                if isinstance(result, list):
                    self.cache.set(adapter_name, result)
                    all_races.extend(result)
                elif result is not None:
                    logger.error(
                        f"Exception for {adapter_name}: {result}", exc_info=result
                    )

        # Sort races by start time
        all_races.sort(key=lambda race: race.get("start_time", ""))
        return all_races

    def save_races_to_json(self, races, filename):
        """Saves race data to a JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(races, f, indent=4)
            logger.info(f"Successfully saved {len(races)} races to {filename}.")
        except IOError as e:
            logger.error(f"Error saving races to {filename}: {e}")


# --- Main Execution ---
async def main():
    """Main function to initialize and run the service."""
    cache = Cache(ttl_seconds=CACHE_TTL_SECONDS)
    circuit_breaker = CircuitBreaker(
        threshold=CIRCUIT_BREAKER_THRESHOLD,
        timeout_seconds=CIRCUIT_BREAKER_TIMEOUT_SECONDS,
    )
    service = RaceService(cache, circuit_breaker)

    races = await service.get_all_races()
    if races:
        service.save_races_to_json(races, OUTPUT_FILENAME)
    else:
        logger.warning("No races were fetched.")


if __name__ == "__main__":
    asyncio.run(main())