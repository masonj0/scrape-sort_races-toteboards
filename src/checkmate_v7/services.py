"""
Checkmate V7: services.py - THE GATEWAY
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
from .base import BaseAdapterV7, DefensiveFetcher
from .adapters.fanduel import FanDuelApiAdapterV7
from .adapters.skysports import SkySportsAdapter
from .adapters.attheraces_adapter import AtTheRacesAdapter

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




class DataSourceOrchestrator:
    def __init__(self, session):
        self.fetcher = DefensiveFetcher()
        self.db_session = session
        self.adapters: List[BaseAdapterV7] = [
            SkySportsAdapter(self.fetcher),
            FanDuelApiAdapterV7(self.fetcher),
            AtTheRacesAdapter(self.fetcher),
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
            process_race_for_prediction.delay(race.dict)

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
