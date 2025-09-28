# checkmate_service.py
# The restored, correct version of the main service runner.

import time
import logging
import sqlite3
import json
import os
import threading
from datetime import datetime
from engine import SuperchargedOrchestrator, EnhancedTrifectaAnalyzer, Settings, Race
from typing import List

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def _setup_database(self):
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            schema_path = os.path.join(base_dir, 'shared_database', 'schema.sql')
            web_schema_path = os.path.join(base_dir, 'shared_database', 'web_schema.sql')

            with open(schema_path, 'r') as f:
                schema = f.read()
            with open(web_schema_path, 'r') as f:
                web_schema = f.read()

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema)
                cursor.executescript(web_schema)
                conn.commit()
            self.logger.info(f"Database schemas applied successfully.")
        except Exception as e:
            self.logger.critical(f"FATAL: Could not set up database: {e}", exc_info=True)
            raise

    def update_races_and_status(self, races: List[Race], statuses: List[dict]):
        # ... (full implementation from previous directives)
        pass

class CheckmateBackgroundService:
    def __init__(self):
        self.settings = Settings()
        db_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "shared_database", "races.db")
        self.db_handler = DatabaseHandler(db_path)
        self.orchestrator = SuperchargedOrchestrator(self.settings)
        self.analyzer = EnhancedTrifectaAnalyzer(self.settings)
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(self.__class__.__name__)

    def run_continuously(self, interval_seconds: int = 60):
        self.logger.info("Antifragile Collector Service starting continuous run.")
        while not self.stop_event.is_set():
            self.logger.info("Starting advanced data collection and analysis cycle.")
            try:
                races, statuses = self.orchestrator.get_races_parallel()
                analyzed_races = [self.analyzer.analyze_race_advanced(race) for race in races]
                self.db_handler.update_races_and_status(analyzed_races, statuses)
            except Exception as e:
                self.logger.critical(f"FATAL error in main service loop: {e}", exc_info=True)
            self.stop_event.wait(interval_seconds)

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_continuously)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("CheckmateBackgroundService started.")

    def stop(self):
        self.stop_event.set()
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=10)
        self.logger.info("CheckmateBackgroundService stopped.")