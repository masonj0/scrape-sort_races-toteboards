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
from typing import List, Optional
from urllib.parse import urlparse

# New dependencies for the Golden Age Fetcher
from curl_cffi.requests import Session as CurlCffiSession
from bs4 import BeautifulSoup
import pandas as pd
from celery import Celery
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from . import config, logic
from .models import AdapterStatusORM, PredictionORM, ResultORM, JoinORM, Base, Race, Runner
from .base import BaseAdapterV7 # DefensiveFetcher is no longer imported from here
from .adapters.fanduel import FanDuelApiAdapterV7
# from .adapters.twinspires_adapter import TwinspiresModernAdapter
# from .adapters.betfair_data_scientist_adapter import BetfairModernAdapter
# from .adapters.racingpost_adapter import RacingPostModernAdapter

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


# --- Golden Age DefensiveFetcher ---
class DefensiveFetcher:
    """
    A resilient, multi-method, 'waterfall' fetcher adapted from the project's
    'Golden Age' source material. It tries different fetching strategies
    sequentially until one succeeds.
    """
    def _try_curl_cffi(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[dict]:
        logging.info(f"Fetcher: Trying curl_cffi for {method} {urlparse(url).netloc}")
        try:
            session = CurlCffiSession(impersonate="chrome120", timeout=20)
            if method == 'POST':
                response = session.post(url, headers=headers, json=json_data, verify=False, timeout=20)
            else:
                response = session.get(url, headers=headers, verify=False, timeout=20)
            response.raise_for_status()
            logging.info("Fetcher: Success with curl_cffi!")
            return response.json()
        except Exception as e:
            logging.warning(f"Fetcher: curl_cffi failed: {str(e)[:150]}")
            return None

    def _try_requests_with_variations(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[dict]:
        logging.info(f"Fetcher: Trying requests for {method} {urlparse(url).netloc}")
        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=json_data, verify=False, timeout=15, allow_redirects=True)
            else:
                response = requests.get(url, headers=headers, verify=False, timeout=15, allow_redirects=True)

            if response.status_code == 200 and response.text:
                logging.info("Fetcher: Success with requests!")
                return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.warning(f"Fetcher: requests failed: {str(e)[:150]}")
            return None
        return None

    def _try_subprocess_curl(self, method: str, url: str, headers: dict, json_data: Optional[dict] = None) -> Optional[dict]:
        logging.info(f"Fetcher: Trying subprocess curl for {method} {urlparse(url).netloc}")
        if not shutil.which("curl"):
            logging.warning("Fetcher: 'curl' command not found in system PATH.")
            return None
        try:
            curl_cmd = ['curl', '--silent', '--show-error', '--location', '--compressed', '--max-time', '30']
            for key, value in headers.items():
                curl_cmd.extend(['--header', f'{key}: {value}'])

            if method == 'POST':
                curl_cmd.extend(['-X', 'POST'])
                if json_data:
                    curl_cmd.extend(['--header', 'Content-Type: application/json'])
                    curl_cmd.extend(['-d', json.dumps(json_data)])

            curl_cmd.append(url)

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=45, check=False)

            if result.returncode == 0 and result.stdout:
                logging.info("Fetcher: Success with subprocess curl!")
                return json.loads(result.stdout)
            else:
                logging.warning(f"Fetcher: Subprocess curl failed with return code {result.returncode}")
                return None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logging.warning(f"Fetcher: Subprocess curl exception: {str(e)[:150]}")
            return None

    def request(self, method: str, url: str, headers: Optional[dict] = None, json_data: Optional[dict] = None) -> dict:
        """
        Primary fetch method that orchestrates the waterfall logic.
        """
        # Default headers if none provided
        final_headers = headers.copy() if headers else {}
        if 'User-Agent' not in final_headers:
            final_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

        # Waterfall through fetching methods
        for fetch_method in [self._try_curl_cffi, self._try_requests_with_variations, self._try_subprocess_curl]:
            result = fetch_method(method, url, final_headers, json_data)
            if result:
                return result
            time.sleep(0.5)

        logging.error(f"Fetcher: All methods failed for {method} {url}")
        return {}

    def get(self, url: str, headers: Optional[dict] = None) -> dict:
        return self.request('GET', url, headers=headers)

    def post(self, url: str, headers: Optional[dict] = None, json_data: Optional[dict] = None) -> dict:
        return self.request('POST', url, headers=headers, json_data=json_data)


class DataSourceOrchestrator:
    def __init__(self, session):
        self.fetcher = DefensiveFetcher()
        self.db_session = session
        self.adapters: List[BaseAdapterV7] = [
            FanDuelApiAdapterV7(self.fetcher),
            # TwinspiresModernAdapter(self.fetcher),
            # BetfairModernAdapter(self.fetcher),
            # RacingPostModernAdapter(self.fetcher),
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

            if races:
                all_races.extend(races)
                break

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
