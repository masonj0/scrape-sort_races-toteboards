# checkmate_service.py
# The main service runner, upgraded to the final Endgame architecture.

import time
import logging
import sqlite3
import json
import os
import threading
from datetime import datetime
from .engine import SuperchargedOrchestrator, EnhancedTrifectaAnalyzer, Settings, Race
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
            # Construct robust paths to both schema files
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
            self.logger.info(f"Database schemas applied successfully from {schema_path} and {web_schema_path}.")
        except Exception as e:
            self.logger.critical(f"FATAL: Could not set up database from schema files: {e}", exc_info=True)
            raise

    def update_races_and_status(self, races: List[Race], statuses: List[dict]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
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
            for status in statuses:
                cursor.execute("""
                    INSERT OR REPLACE INTO adapter_status (adapter_name, status, last_run, races_found, error_message, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    status.get('adapter_id'), status.get('status'), status.get('timestamp'),
                    status.get('races_found'), status.get('error_message'), int(status.get('response_time', 0) * 1000)
                ))

            if races or statuses:
                cursor.execute("INSERT INTO events (event_type, payload) VALUES (?, ?)",
                               ('RACES_UPDATED', json.dumps({'race_count': len(races)})))

            conn.commit()
        self.logger.info(f"Database updated with {len(races)} races and {len(statuses)} adapter statuses.")

class CheckmateBackgroundService:
    def __init__(self):
        self.settings = Settings()
        self.db_handler = DatabaseHandler(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "shared_database", "races.db"))
        self.orchestrator = SuperchargedOrchestrator(self.settings)
        self.analyzer = EnhancedTrifectaAnalyzer(self.settings)
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(self.__class__.__name__)

    def run_continuously(self, interval_seconds: int = 60):
        self.logger.info("Supercharged background service starting continuous run.")
        while not self.stop_event.is_set():
            self.logger.info("Starting advanced data collection and analysis cycle.")
            try:
                races, statuses = self.orchestrator.get_races_parallel()
                analyzed_races = [self.analyzer.analyze_race_advanced(race) for race in races]
                self.db_handler.update_races_and_status(analyzed_races, statuses)
            except Exception as e:
                self.logger.critical(f"FATAL error in main service loop: {e}", exc_info=True)

            self.stop_event.wait(interval_seconds)

                    res = results_map[race.race_id]
                    race.checkmate_score = res.get('checkmate_score')
                    race.is_qualified = res.get('qualified')
                    race.trifecta_factors_json = json.dumps(res.get('trifecta_factors'))
            return races
        except FileNotFoundError:
            self.logger.warning("Rust engine not found. Falling back to Python analyzer.")
            return None
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Rust engine execution failed: {e}. Falling back to Python analyzer.")
            return None

    def _analyze_with_python(self, races: List[Race]) -> List[Race]:
        self.logger.info("Performing analysis with internal Python engine.")
        return [self.python_analyzer.analyze_race(race, self.settings) for race in races]

    def run_continuously(self, interval_seconds: int = 60):
        self.logger.info("Background service thread starting continuous run.")

        while not self.stop_event.is_set():
            try:
                self.logger.info("Starting data collection and analysis cycle.")
                races, statuses = self.orchestrator.get_races()

                analyzed_races = None
                if os.path.exists(self.rust_engine_path):
                    analyzed_races = self._analyze_with_rust(races)

                if analyzed_races is None: # Fallback condition
                    analyzed_races = self._analyze_with_python(races)

                if analyzed_races: # Ensure we have something to update
                    self.db_handler.update_races_and_status(analyzed_races, statuses)

            except Exception as e:
                self.logger.critical(f"Unhandled exception in service loop: {e}", exc_info=True)

            self.logger.info(f"Cycle complete. Sleeping for {interval_seconds} seconds.")
            self.stop_event.wait(interval_seconds)
        self.logger.info("Background service run loop has terminated.")


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