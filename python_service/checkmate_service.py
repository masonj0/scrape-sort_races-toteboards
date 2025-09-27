# checkmate_service.py
# Activates the full production engine.

import time
import logging
import sqlite3
import json
from datetime import datetime
from engine import DataSourceOrchestrator, TrifectaAnalyzer, Settings, Race
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
            # The schema file path is relative to where the service is run.
            # Assuming it runs from the `python_service` directory.
            with open('../shared_database/schema.sql', 'r') as f:
                schema = f.read()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema)
                conn.commit()
            self.logger.info("Database schema applied successfully from schema.sql.")
        except Exception as e:
            self.logger.critical(f"FATAL: Could not set up database from schema file: {e}", exc_info=True)
            raise

    def update_races_and_status(self, races: List[Race], statuses: List[dict]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Update races
            for race in races:
                cursor.execute("""
                    INSERT OR REPLACE INTO live_races
                    (race_id, track_name, race_number, post_time, raw_data_json, checkmate_score, qualified, trifecta_factors_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    race.race_id, race.track_name, race.race_number, race.post_time,
                    race.model_dump_json(), race.checkmate_score, race.is_qualified,
                    race.trifecta_factors_json, datetime.now()
                ))
            # Update adapter statuses
            for status in statuses:
                cursor.execute("""
                    INSERT OR REPLACE INTO adapter_status (adapter_name, status, last_run, races_found, error_message, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    status.get('adapter_id'), status.get('status'), status.get('timestamp'),
                    status.get('races_found'), status.get('error_message'), int(status.get('response_time', 0) * 1000)
                ))
            conn.commit()
        self.logger.info(f"Database updated with {len(races)} races and {len(statuses)} adapter statuses.")

class CheckmateBackgroundService:
    def __init__(self):
        # Path is relative to the execution directory of the service wrapper
        self.db_path = "..\\shared_database\\races.db"
        self.db_handler = DatabaseHandler(self.db_path)
        self.orchestrator = DataSourceOrchestrator()
        self.analyzer = TrifectaAnalyzer()
        self.settings = Settings()
        self.running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def run_continuously(self, interval_seconds: int = 60):
        self.running = True
        self.logger.info("Background service starting continuous run with full engine.")
        while self.running:
            self.logger.info("Starting live data collection and analysis cycle.")
            races, statuses = self.orchestrator.get_races()
            analyzed_races = [self.analyzer.analyze_race(race, self.settings) for race in races]
            self.db_handler.update_races_and_status(analyzed_races, statuses)
            self.logger.info(f"Cycle complete. Sleeping for {interval_seconds} seconds.")
            time.sleep(interval_seconds)

    def stop(self):
        self.running = False
        self.logger.info("Background service stopping.")