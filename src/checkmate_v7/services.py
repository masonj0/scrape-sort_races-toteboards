"""
Checkmate V7: `services.py` - THE GATEWAY
"""
import logging
import asyncio
import random
import time
import anyio
import json
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup
from celery import Celery
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from . import config, logic
from .models import AdapterStatusORM, PredictionORM, ResultORM, JoinORM, Base, Race, Runner
from .base import DefensiveFetcher, BaseAdapterV7
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
    """
    This function is connected to Celery's logging signals and
    reconfigures the logger to use our structured JSON format.
    """
    # Use the same handlers from the root logger
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)

    logger.propagate = False

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
        """
        Iterates through adapters, attempting to fetch races and returning
        both the race data and a detailed status report.
        """
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
    """The main entry point task for the Prediction Engine."""
    logging.info("Starting prediction cycle...")
    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        races, statuses = orchestrator.get_races()

        logging.info(f"Adapter statuses: {statuses}")
        logging.info(f"Found {len(races)} races to process.")

        for race in races:
            # Convert dataclass to dict for Celery serialization
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
    """Analyzes a single race and saves a prediction if it qualifies."""
    # This task is now designed to be called by the main cycle
    session = get_db_session()
    try:
        # The race data would be a dict here, needs to be reconstructed
        # For now, we'll just log it.
        logging.info(f"Processing race: {race_data.get('track')} R{race_data.get('race_number')}")
        # analyzer = logic.AdvancedPlaceBetAnalyzer() # When implemented
        # analysis = analyzer.analyze(race_data)
        # if analysis.should_bet:
        #     # db_manager.save_prediction(analysis)
        #     pass
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3)
def run_audit_cycle(self):
    """The main entry point task for the Historian Engine."""
    logging.info("Starting audit cycle...")
    session = None
    try:
        session = get_db_session()
        pending_predictions = session.query(PredictionORM).filter_by(status='pending').all()
        logging.info(f"Found {len(pending_predictions)} pending predictions to audit.")
        for pred in pending_predictions:
            # Check if race time has passed
            # For now, we just queue all pending
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
    """Fetches results for a single race and creates an audit record."""
    logging.info(f"Fetching results for {race_key}...")
    # In a real implementation, this would fetch real results and
    # create a real audit record. For now, it's a placeholder.
    pass
