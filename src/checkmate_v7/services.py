"""
Checkmate V7: `services.py` - THE GATEWAY
"""
import logging
import asyncio
import random
import time
import aiohttp
from celery import Celery
from .models import AdapterStatusORM
from . import logic

from . import config

# --- Celery App Configuration ---
celery_app = Celery('tasks', broker=config.REDIS_URL)

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    async def __aenter__(self):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.last_failure_time = time.time()
        elif self.state == "half-open":
            self.failure_count = 0
            self.state = "closed"

class DefensiveFetcher:
    def __init__(self):
        self.circuit_breakers = {}

    async def fetch(self, url, headers=None):
        domain = url.split('/')[2]
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = CircuitBreaker()

        cb = self.circuit_breakers[domain]

        retries = 5
        for i in range(retries):
            try:
                async with cb:
                    async with aiohttp.ClientSession(headers=headers) as session:
                        # "think_time_ms"
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                        async with session.get(url, timeout=15) as response:
                            response.raise_for_status()
                            return await response.text()
            except Exception as e:
                logging.warning(f"Attempt {i+1}/{retries} failed for {url}: {e}")
                if i < retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** i) + random.uniform(0, 1)
                    logging.info(f"Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"All retries failed for {url}")
                    raise

class DataSourceOrchestrator:
    def __init__(self, session):
        self.fetcher = DefensiveFetcher()
        self.db_session = session
        self.adapter_priority = ["test_data", "twinspires", "rpb2b"] # Test data first

    async def get_races(self):
        # In a real implementation, this would check the health of adapters
        # from the database using AdapterStatusORM and the db_session.
        for adapter_name in self.adapter_priority:
            logging.info(f"Attempting to fetch races from {adapter_name}")
            try:
                if adapter_name == "test_data":
                    return logic.get_test_data()
                # Placeholders for real adapters
                elif adapter_name == "twinspires":
                    # races = await self.fetcher.fetch(...)
                    pass
                elif adapter_name == "rpb2b":
                    pass

            except Exception as e:
                logging.error(f"Failed to fetch from {adapter_name}: {e}")
                # Here we would update the adapter status in the DB
                continue
        return []

from .models import PredictionORM, ResultORM, JoinORM, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_session():
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

from sqlalchemy.exc import SQLAlchemyError

@celery_app.task(bind=True, max_retries=3)
def run_prediction_cycle(self):
    """The main entry point task for the Prediction Engine."""
    logging.info("Starting prediction cycle...")
    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        races = asyncio.run(orchestrator.get_races())

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
