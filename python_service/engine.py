# engine.py
# Forged for the Desktop Supremacy Campaign

import logging
import json
import subprocess
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class Runner(BaseModel):
    name: str
    odds: Optional[float] = None
    program_number: Optional[int] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    runners: List[Runner]
    source: Optional[str] = None

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _setup_database(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS live_races (
                        race_id TEXT PRIMARY KEY,
                        track_name TEXT,
                        post_time DATETIME,
                        source TEXT,
                        data_json TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
            self.logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            self.logger.critical(f"FATAL: Could not set up database: {e}", exc_info=True)
            raise