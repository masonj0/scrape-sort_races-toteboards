# src/checkmate_v7/base.py
import logging
from typing import List, Optional, Union
import requests
from curl_cffi.requests import Session as CurlCffiSession, Response
from .models import Race

class DefensiveFetcher:
    def get(self, url: str, response_type: str = 'text') -> Union[dict, str, None]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        try:
            session = CurlCffiSession(impersonate="chrome110")
            response = session.get(url, headers=headers, verify=False, timeout=20)
            response.raise_for_status()
            return response.json() if response_type == 'json' else response.text
        except Exception:
            try:
                response = requests.get(url, headers=headers, verify=False, timeout=15)
                response.raise_for_status()
                return response.json() if response_type == 'json' else response.text
            except Exception as e:
                logging.error(f"All GET methods failed for {url}: {e}")
                return None

    def post(self, url: str, json_data: Optional[dict] = None, response_type: str = 'json') -> Union[dict, str, None]:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        try:
            session = CurlCffiSession(impersonate="chrome110")
            response = session.post(url, headers=headers, json=json_data, verify=False, timeout=20)
            response.raise_for_status()
            return response.json() if response_type == 'json' else response.text
        except Exception:
            try:
                response = requests.post(url, headers=headers, json=json_data, verify=False, timeout=15)
                response.raise_for_status()
                return response.json() if response_type == 'json' else response.text
            except Exception as e:
                logging.error(f"All POST methods failed for {url}: {e}")
                return None

class BaseAdapterV7:
    SOURCE_ID = "base"
    def __init__(self, fetcher: DefensiveFetcher):
        self.fetcher = fetcher
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError