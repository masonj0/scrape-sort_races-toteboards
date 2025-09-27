# engine.py
# Forged according to the Hardening Protocols

import logging
import json
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# --- Professional Settings Management ---
class Settings(BaseSettings):
    QUALIFICATION_SCORE: float = Field(default=75.0)
    FIELD_SIZE_OPTIMAL_MIN: int = Field(default=4)
    FIELD_SIZE_OPTIMAL_MAX: int = Field(default=6)
    FIELD_SIZE_ACCEPTABLE_MIN: int = Field(default=7)
    FIELD_SIZE_ACCEPTABLE_MAX: int = Field(default=8)
    FIELD_SIZE_OPTIMAL_POINTS: int = Field(default=30)
    FIELD_SIZE_ACCEPTABLE_POINTS: int = Field(default=10)
    FIELD_SIZE_PENALTY_POINTS: int = Field(default=-20)
    FAV_ODDS_POINTS: int = Field(default=30)
    MAX_FAV_ODDS: float = Field(default=3.5)
    SECOND_FAV_ODDS_POINTS: int = Field(default=40)
    MIN_2ND_FAV_ODDS: float = Field(default=4.0)

# --- Data Models ---
class Runner(BaseModel):
    name: str
    odds: Optional[float] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    runners: List[Runner]
    source: Optional[str] = None
    checkmate_score: Optional[float] = None
    is_qualified: Optional[bool] = None

# --- Hardened Database Handler ---
class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_database()

    def _get_connection(self):
        # timeout parameter helps with SQLITE_BUSY errors
        return sqlite3.connect(self.db_path, timeout=10)

    def _setup_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 'live_races' table now includes pre-calculated results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_races (
                    race_id TEXT PRIMARY KEY,
                    track_name TEXT,
                    post_time DATETIME,
                    source TEXT,
                    checkmate_score REAL,
                    is_qualified INTEGER,
                    data_json TEXT,
                    updated_at DATETIME
                );
            """)
            # 'events' table for the 'Reliable Trigger' protocol
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            self.logger.info(f"Hardened database initialized successfully at {self.db_path}")

    def update_races(self, races: List[Race]):
        # This method will be expanded with retry logic
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for race in races:
                cursor.execute("""
                    INSERT OR REPLACE INTO live_races
                    (race_id, track_name, post_time, source, checkmate_score, is_qualified, data_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    race.race_id, race.track_name, race.post_time, race.source,
                    race.checkmate_score, race.is_qualified,
                    race.model_dump_json(), datetime.now()
                ))
            # Fire the reliable trigger for the C# app
            cursor.execute("""
                INSERT INTO events (event_type, payload) VALUES (?, ?)
            """, ("RACES_UPDATED", json.dumps({"race_count": len(races)})))
            conn.commit()

# --- Trifecta Analyzer (Engine Does the Thinking) ---
class TrifectaAnalyzer:
    def analyze_race(self, race: Race, settings: Settings) -> Race:
        # Placeholder for the full analysis logic
        # In the real implementation, this will calculate the score and qualification
        race.checkmate_score = 50.0 # Dummy score
        race.is_qualified = race.checkmate_score >= settings.QUALIFICATION_SCORE
        return race