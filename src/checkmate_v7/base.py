import logging
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Union
from .models import Race

class DefensiveFetcher:
    """The battle-tested, subprocess curl-based fetcher."""

    def get(self, url: str, headers: dict = None, response_type: str = 'auto') -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1"] # Enforce modern standards
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)

            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout

            if response_type == 'text':
                return response_text
            if response_type == 'json':
                return json.loads(response_text)

            # Auto-detect for 'auto'
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return response_text

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

    def post(self, url: str, json_data: dict, headers: dict = None, response_type: str = 'json') -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "-X", "POST", "--tlsv1.2", "--http1.1"]
            final_headers = headers.copy() if headers else {}
            final_headers['Content-Type'] = 'application/json'

            for key, value in final_headers.items():
                command.extend(["-H", f"{key}: {value}"])

            command.extend(["-d", json.dumps(json_data)])
            command.append(url)

            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout

            return json.loads(response_text) if response_type == 'json' else response_text

        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.error(f"CRITICAL: curl POST failed for {url}. Details: {e}")
            return None

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher

    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError