"""
Checkmate V7: `base.py` - Core abstractions and base classes.
"""
import logging
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List

# Moved from services.py to break circular dependency
from .models import Race


class DefensiveFetcher:
    """
    An "Ironclad" Fetcher that uses curl via subprocess to bypass environment
    issues with Python's HTTP libraries. This is a synchronous implementation.
    """
    def fetch(self, url: str, headers: dict = None) -> dict:
        """
        Performs a GET request using curl and returns parsed JSON.
        """
        try:
            command = ["curl", "-s", "-L"]
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            logging.error(f"ERROR: curl GET command failed for {url}. Details: {e}")
            return {}

    def post(self, url: str, json_data: dict, headers: dict = None) -> dict:
        """
        Performs a POST request with a JSON payload using curl.
        """
        try:
            command = ["curl", "-s", "-L", "-X", "POST"]

            # Add headers, ensuring Content-Type is set for JSON
            final_headers = headers.copy() if headers else {}
            final_headers['Content-Type'] = 'application/json'

            for key, value in final_headers.items():
                command.extend(["-H", f"{key}: {value}"])

            command.extend(["-d", json.dumps(json_data)])
            command.append(url)

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            logging.error(f"ERROR: curl POST command failed for {url}. Details: {e}")
            return {}


class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher

    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError
