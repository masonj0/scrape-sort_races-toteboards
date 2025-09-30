#!/usr/bin/env python3
# ==============================================================================
# Checkmate V8 - Production Tipsheet Generator
# ==============================================================================
# Fully integrated with the Penta-Hybrid architecture.
# Generates CSV tipsheets from qualified races in the shared database.
# This script is a read-only consumer of the main data pipeline.
# ==============================================================================

import csv
import json
import sqlite3
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# ==============================================================================
# Configuration
# ==============================================================================

class Config:
    """Configuration for tipsheet generation."""
    BASE_DIR = Path(__file__).parent.resolve()
    DB_PATH = BASE_DIR / "shared_database" / "races.db"
    OUTPUT_DIR = BASE_DIR / "output"
    OUTPUT_CSV = OUTPUT_DIR / f"tipsheet_{datetime.now():%Y%m%d_%H%M%S}.csv"
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    MAX_RACES_IN_TIPSHEET = 50

CONFIG = Config()

# ==============================================================================
# Logging Setup
# ==============================================================================

logging.basicConfig(
    level=CONFIG.LOG_LEVEL,
    format=CONFIG.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CONFIG.BASE_DIR / 'tipsheet_generator.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

# ==============================================================================
# Data Models & Database Operations
# ==============================================================================

class RaceTipsheet:
    """Represents a race for tipsheet output."""
    def __init__(self, row: sqlite3.Row):
        self.race_id: str = row['race_id']
        self.track_name: str = row['track_name']
        self.race_number: Optional[int] = row['race_number']
        self.post_time: Optional[datetime] = self._parse_datetime(row['post_time'])
        self.checkmate_score: float = row['checkmate_score']
        self.trifecta_factors: dict = self._parse_json(row['trifecta_factors_json'])
        self.raw_data: dict = self._parse_json(row['raw_data_json'])

    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        if not dt_str: return None
        try: return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError): return None

    @staticmethod
    def _parse_json(json_str: Optional[str]) -> dict:
        if not json_str: return {}
        try: return json.loads(json_str)
        except (json.JSONDecodeError, TypeError): return {}

    def get_post_time_formatted(self) -> str:
        return self.post_time.strftime('%I:%M %p') if self.post_time else 'TBD'

    def get_trifecta_summary(self) -> str:
        summaries = [f"✓ {k}: {v.get('reason', '')} ({v.get('points', 0):+.0f} pts)" for k, v in self.trifecta_factors.items() if isinstance(v, dict) and v.get('ok')]
        return " | ".join(summaries) if summaries else "No positive factors"

    def get_runner_count(self) -> int:
        return len(self.raw_data.get('runners', []))

class DatabaseManager:
    """Handles all database operations."""
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get_qualified_races(self, limit: int) -> List[RaceTipsheet]:
        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            return []
        races = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM live_races WHERE qualified = 1 ORDER BY checkmate_score DESC, post_time ASC LIMIT ?", (limit,))
                for row in cursor:
                    races.append(RaceTipsheet(row))
            logger.info(f"Retrieved {len(races)} qualified races from database")
        except sqlite3.Error as e:
            logger.error(f"Database query failed: {e}")
        return races

# ==============================================================================
# CSV Generation
# ==============================================================================

class TipsheetGenerator:
    """Generates CSV tipsheets from qualified races."""
    def __init__(self, output_path: Path):
        self.output_path = output_path

    def generate_csv(self, races: List[RaceTipsheet]) -> bool:
        if not races: logger.warning("No races to write to CSV"); return False
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Track', 'Race', 'Post Time', 'Score', 'Runners', 'Analysis Summary', 'Race ID'])
                for race in races:
                    writer.writerow([
                        race.track_name, f"R{race.race_number}", race.get_post_time_formatted(),
                        f"{race.checkmate_score:.1f}", race.get_runner_count(),
                        race.get_trifecta_summary(), race.race_id
                    ])
            logger.info(f"CSV tipsheet generated: {self.output_path}")
            return True
        except IOError as e:
            logger.error(f"Failed to write CSV: {e}")
            return False

# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main execution function."""
    logger.info("Starting tipsheet generation")
    db_manager = DatabaseManager(CONFIG.DB_PATH)
    races = db_manager.get_qualified_races(limit=CONFIG.MAX_RACES_IN_TIPSHEET)
    if not races:
        logger.warning("No qualified races found in database. Exiting.")
        print("\n⚠️  WARNING: No qualified races available to generate a tipsheet.")
        sys.exit(0)

    generator = TipsheetGenerator(CONFIG.OUTPUT_CSV)
    if generator.generate_csv(races):
        print(f"\n✅ Success! Tipsheet generated at: {CONFIG.OUTPUT_CSV}")
    else:
        print("\n❌ ERROR: Failed to generate tipsheet.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)