"""
Checkmate V7: `services.py` - THE GATEWAY
"""
import logging
import time
import json
import re
import random
import subprocess
import shutil
import requests
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from typing import List, Optional, Union
from urllib.parse import urlparse

# New dependencies for the Golden Age Fetcher
from curl_cffi.requests import Session as CurlCffiSession, Response
from bs4 import BeautifulSoup
import pandas as pd
from celery import Celery
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from . import config, logic
from .models import AdapterStatusORM, PredictionORM, ResultORM, JoinORM, Base, Race, Runner
from .base import BaseAdapterV7
from .adapters.fanduel import FanDuelApiAdapterV7
from .adapters.skysports import SkySportsAdapter

# --- Celery App Configuration ---
celery_app = Celery('tasks', broker=config.REDIS_URL)

# --- Celery Logging Integration ---
from celery.signals import after_setup_logger, after_setup_task_logger

@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logging(logger, **kwargs):
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)
    logger.propagate = False


# --- The Universal DefensiveFetcher (V3 - Phoenix Edition) ---
class DefensiveFetcher:
    """
    The definitive, universal, multi-method fetcher. It handles both JSON APIs
    and HTML scraping by allowing the caller to specify the expected response type.
    """
    def _try_curl_cffi(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[Response]:
        logging.info(f"Fetcher: Trying curl_cffi for {method} {urlparse(url).netloc}")
        try:
            session = CurlCffiSession(impersonate="chrome110", timeout=20)
            if method == 'POST':
                response = session.post(url, headers=headers, json=json_data, verify=False, timeout=20)
            else:
                response = session.get(url, headers=headers, verify=False, timeout=20)
            response.raise_for_status()
            logging.info("Fetcher: Success with curl_cffi!")
            return response
        except Exception as e:
            logging.warning(f"Fetcher: curl_cffi failed: {str(e)[:150]}")
            return None

    def _try_requests(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[requests.Response]:
        logging.info(f"Fetcher: Trying requests for {method} {urlparse(url).netloc}")
        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=json_data, verify=False, timeout=15, allow_redirects=True)
            else:
                response = requests.get(url, headers=headers, verify=False, timeout=15, allow_redirects=True)

            response.raise_for_status()
            logging.info("Fetcher: Success with requests!")
            return response
        except requests.exceptions.RequestException as e:
            logging.warning(f"Fetcher: requests failed: {str(e)[:150]}")
            return None

    def _try_subprocess_curl(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[str]:
        logging.info(f"Fetcher: Trying subprocess curl for {method} {urlparse(url).netloc}")
        if not shutil.which("curl"):
            logging.warning("Fetcher: 'curl' command not found in system PATH.")
            return None
        try:
            curl_cmd = ['curl', '-s', '-L', '--show-error', '--compressed', '--max-time', '30']
            for key, value in headers.items():
                curl_cmd.extend(['-H', f'{key}: {value}'])

            if method == 'POST':
                curl_cmd.extend(['-X', 'POST'])
                if json_data:
                    curl_cmd.extend(['-H', 'Content-Type: application/json'])
                    curl_cmd.extend(['-d', json.dumps(json_data)])

            curl_cmd.append(url)

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=45, check=True)
            logging.info("Fetcher: Success with subprocess curl!")
            return result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.warning(f"Fetcher: Subprocess curl failed or timed out: {e}")
            return None

    def request(self, method: str, url: str, headers: Optional[dict] = None, json_data: Optional[dict] = None, response_type: str = 'json') -> Union[dict, str]:
        """
        Primary fetch method. Tries multiple strategies and returns the content
        in the format specified by `response_type`.
        """
        final_headers = headers.copy() if headers else {}
        if 'User-Agent' not in final_headers:
            final_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

        # --- Waterfall Stage 1 & 2: Python Libraries ---
        for fetch_method in [self._try_curl_cffi, self._try_requests]:
            response = fetch_method(method, url, final_headers, json_data)
            if response:
                try:
                    if response_type == 'json':
                        return response.json()
                    else:
                        return response.text
                except json.JSONDecodeError as e:
                    logging.warning(f"Fetcher: Failed to decode {response_type} from {fetch_method.__name__}: {e}")
                    continue # Try the next method

        # --- Waterfall Stage 3: System Subprocess (already returns text) ---
        text_response = self._try_subprocess_curl(method, url, final_headers, json_data)
        if text_response:
            if response_type == 'json':
                try:
                    return json.loads(text_response)
                except json.JSONDecodeError as e:
                     logging.error(f"Fetcher: Final method (subprocess) succeeded but failed to parse JSON: {e}")
                     return {}
            else:
                return text_response

        logging.error(f"Fetcher: All methods failed for {method} {url}")
        return {} if response_type == 'json' else ""

    def get(self, url: str, headers: Optional[dict] = None, response_type: str = 'json') -> Union[dict, str]:
        return self.request('GET', url, headers=headers, response_type=response_type)

    def post(self, url: str, headers: Optional[dict] = None, json_data: Optional[dict] = None, response_type: str = 'json') -> Union[dict, str]:
        return self.request('POST', url, headers=headers, json_data=json_data, response_type=response_type)


class DataSourceOrchestrator:
    def __init__(self, session):
        self.fetcher = DefensiveFetcher()
        self.db_session = session
        self.adapters: List[BaseAdapterV7] = [
            SkySportsAdapter(self.fetcher),
            FanDuelApiAdapterV7(self.fetcher),
        ]

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races = []
        statuses = []
        for adapter in self.adapters:
            adapter_id = adapter.__class__.__name__
            races = []
            error_message = None
            status = "OK"
            notes = ""

            try:
                races = adapter.fetch_races()
                if races:
                    notes = f"Successfully parsed {len(races)} races."
                    logging.info(notes)
                    all_races.extend(races) # Keep collecting races
                else:
                    notes = "No upcoming races found on source."
                    logging.info(notes)
            except Exception as e:
                logging.error(f"Failed to fetch from {adapter_id}: {e}", exc_info=True)
                status = "ERROR"
                error_message = str(e)
                notes = f"API Error: {error_message}"

            statuses.append({
                "adapter_id": adapter_id,
                "status": status,
                "races_found": len(races),
                "error_message": error_message,
                "notes": notes,
                "last_run": datetime.now(timezone.utc).isoformat()
            })

            # As per user request, don't break, let all adapters run
            # if races:
            #     break

        return all_races, statuses

def get_db_session():
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

@celery_app.task(bind=True, max_retries=3)
def run_prediction_cycle(self):
    logging.info("Starting prediction cycle...")
    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        races, statuses = orchestrator.get_races()

        logging.info(f"Adapter statuses: {statuses}")
        logging.info(f"Found {len(races)} races to process.")

        for race in races:
            process_race_for_prediction.delay(race.__dict__)

    except SQLAlchemyError as e:
        logging.error("Database error during prediction cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=60)
    except Exception as e:
        logging.error("An unexpected error occurred during prediction cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=60)
    finally:
        if session:
            session.close()

@celery_app.task
def process_race_for_prediction(race_data: dict):
    session = get_db_session()
    try:
        logging.info(f"Processing race: {race_data.get('track')} R{race_data.get('race_number')}")
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3)
def run_audit_cycle(self):
    logging.info("Starting audit cycle...")
    session = None
    try:
        session = get_db_session()
        pending_predictions = session.query(PredictionORM).filter_by(status='pending').all()
        logging.info(f"Found {len(pending_predictions)} pending predictions to audit.")
        for pred in pending_predictions:
            process_race_for_results.delay(pred.race_key)
    except SQLAlchemyError as e:
        logging.error("Database error during audit cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=300)
    except Exception as e:
        logging.error("An unexpected error occurred during audit cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=300)
    finally:
        if session:
            session.close()


@celery_app.task
def process_race_for_results(race_key: str):
    logging.info(f"Fetching results for {race_key}...")
    pass
