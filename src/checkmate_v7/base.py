# src/checkmate_v7/base.py
import logging
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Union
from .models import Race

class DefensiveFetcher:
    def fetch(self, url: str, headers: dict = None) -> Union[dict, str]:
        return self.get(url, headers=headers)

    def get(self, url: str, headers: dict = None, response_type: str = 'auto') -> Union[dict, str]:
        try:
            command = ["curl", "-s", "-L"]
            if headers:
                for key, value in headers.items(): command.extend(["-H", f"{key}: {value}"])
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout
            if response_type == 'text': return response_text
            if response_type == 'json': return json.loads(response_text)
            try: return json.loads(response_text)
            except json.JSONDecodeError: return response_text
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"ERROR: curl GET failed for {url}. Details: {e}")
            return {} if response_type in ['json', 'auto'] else ""

    def post(self, url: str, json_data: dict, headers: dict = None, response_type: str = 'json') -> Union[dict, str]:
        try:
            command = ["curl", "-s", "-L", "-X", "POST"]
            final_headers = headers.copy() if headers else {}
            final_headers['Content-Type'] = 'application/json'
            for key, value in final_headers.items(): command.extend(["-H", f"{key}: {value}"])
            command.extend(["-d", json.dumps(json_data)])
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout
            return json.loads(response_text) if response_type == 'json' else response_text
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            logging.error(f"ERROR: curl POST failed for {url}. Details: {e}")
            return {} if response_type == 'json' else ""

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher
    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError