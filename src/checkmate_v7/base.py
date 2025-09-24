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


from curl_cffi import requests

class DefensiveFetcher:
    """
    An "Ironclad" Fetcher that uses curl via subprocess to bypass environment
    issues with Python's HTTP libraries. This is a synchronous implementation.
    """

    def get(self, url: str, headers: dict = None, response_type: str = "json"):
        """
        Performs a GET request using curl.
        """
        try:
            response = requests.get(url, headers=headers, impersonate="chrome110", timeout=60)
            response.raise_for_status()
            if response_type == "text":
                return response.text
            return response.json()
        except Exception as e:
            logging.error(f"ERROR: curl GET command failed for {url}. Details: {e}")
            if response_type == "text":
                return ""
            return {}

    def post(
        self,
        url: str,
        json_data: dict,
        headers: dict = None,
        response_type: str = "json",
    ):
        """
        Performs a POST request with a JSON payload using curl.
        """
        try:
            command = ["curl", "-s", "-L", "-X", "POST"]

            # Add headers, ensuring Content-Type is set for JSON
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.extend(["-H", "Content-Type: application/json"])

            command.extend(["-d", json.dumps(json_data)])
            command.append(url)

            result = subprocess.run(
                command, capture_output=True, text=True, check=True, timeout=60
            )
            if response_type == "text":
                return result.stdout
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logging.error(
                f"ERROR: Failed to decode JSON from {url}. Details: {e}\nResponse: {result.stdout}"
            )
            return {}
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"ERROR: curl POST command failed for {url}. Details: {e}")
            if response_type == "text":
                return ""
            return {}


class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher

    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError
