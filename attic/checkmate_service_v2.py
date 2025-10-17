import asyncio
import json
import logging
from datetime import datetime

import aiohttp
import async_timeout

# Constants
ADAPTER_MODULES = {
    "betfair_adapter": "BetfairAdapter",
    "betfair_greyhound_adapter": "BetfairGreyhoundAdapter",
    "ladbrokes_adapter": "LadbrokesAdapter",
    "sportsbet_adapter": "SportsbetAdapter",
    "pointsbet_adapter": "PointsbetAdapter",
    "tab_adapter": "TABAdapter",
    "bluebet_adapter": "BlueBetAdapter",
    "unibet_adapter": "UnibetAdapter",
    "palmerbet_adapter": "PalmerbetAdapter",
}
CACHE_TTL = 300  # 5 minutes
CIRCUIT_BREAKER_THRESHOLD = 3
CIRCUIT_BREAKER_TIMEOUT = 60  # 60 seconds
LOG_LEVEL = logging.INFO
REQUEST_TIMEOUT = 10  # 10 seconds

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")

# In-memory cache with TTL
cache = {}

# Circuit breaker state
circuit_breaker_state = {
    "is_open": False,
    "failure_count": 0,
    "last_failure_time": None,
}


async def fetch_with_circuit_breaker(session, url):
    """Fetches data from a URL with a circuit breaker."""
    if circuit_breaker_state["is_open"]:
        if (
            datetime.now() - circuit_breaker_state["last_failure_time"]
        ).total_seconds() > CIRCUIT_BREAKER_TIMEOUT:
            circuit_breaker_state["is_open"] = False  # Half-open state
        else:
            raise ConnectionError("Circuit breaker is open")

    try:
        async with async_timeout.timeout(REQUEST_TIMEOUT):
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                circuit_breaker_state["failure_count"] = 0  # Reset on success
                return data
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        circuit_breaker_state["failure_count"] += 1
        circuit_breaker_state["last_failure_time"] = datetime.now()
        if circuit_breaker_state["failure_count"] >= CIRCUIT_BREAKER_THRESHOLD:
            circuit_breaker_state["is_open"] = True
        raise ConnectionError(f"Failed to fetch data: {e}") from e


async def get_races(session, adapter_name):
    """Gets races from a specific adapter, using cache if available."""
    now = datetime.now()
    if (
        adapter_name in cache
        and (now - cache[adapter_name]["timestamp"]).total_seconds() < CACHE_TTL
    ):
        return cache[adapter_name]["data"]

    adapter_class = getattr(__import__(adapter_name), ADAPTER_MODULES[adapter_name])
    adapter = adapter_class()
    races = await adapter.get_races(session)
    cache[adapter_name] = {"data": races, "timestamp": now}
    return races


async def main():
    """Main function to fetch and process race data."""
    async with aiohttp.ClientSession() as session:
        tasks = [get_races(session, adapter_name) for adapter_name in ADAPTER_MODULES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_races = []
        for result in results:
            if isinstance(result, list):
                all_races.extend(result)
            else:
                logging.error(f"Error fetching races: {result}")

        # Sort races by start time
        all_races.sort(key=lambda race: race["start_time"])

        # Output to a JSON file
        with open("races.json", "w") as f:
            json.dump(all_races, f, indent=4)
        logging.info("Successfully fetched and sorted races.")


if __name__ == "__main__":
    asyncio.run(main())