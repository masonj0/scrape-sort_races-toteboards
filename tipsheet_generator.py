# ==============================================================================
# == Checkmate V8 - INTEGRATED Tipsheet Generator
# ==============================================================================
# Now uses the main engine and database schema for perfect integration
# ==============================================================================

import csv
import json
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from python_service
sys.path.insert(0, str(Path(__file__).parent / "python_service"))

from engine import DataSourceOrchestrator, TrifectaAnalyzer, Settings, Race

# --- Configuration ---
class Config:
    """Centralized configuration matching main system."""
    BASE_DIR = Path(__file__).parent
    DB_PATH = BASE_DIR / "shared_database" / "races.db"
    OUTPUT_CSV_PATH = BASE_DIR / "race_tipsheet.csv"
    QUALIFICATION_SCORE = 75.0

CONFIG = Config()

# --- Database Operations ---
def ensure_database_exists():
    """Ensure the database exists with proper schema."""
    if not CONFIG.DB_PATH.parent.exists():
        CONFIG.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    schema_path = CONFIG.BASE_DIR / "shared_database" / "schema.sql"

    if not schema_path.exists():
        print(f"[ERROR] Schema file not found: {schema_path}")
        return False

    with open(schema_path, 'r') as f:
        schema = f.read()

    with sqlite3.connect(CONFIG.DB_PATH) as conn:
        conn.executescript(schema)

    print(f"[INFO] Database ready at: {CONFIG.DB_PATH}")
    return True

def get_qualified_races_from_db():
    """Retrieve qualified races from the main database."""
    try:
        with sqlite3.connect(CONFIG.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT race_id, track_name, race_number, post_time,
                       checkmate_score, trifecta_factors_json, raw_data_json
                FROM live_races
                WHERE qualified = 1
                ORDER BY checkmate_score DESC, post_time ASC
            """)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERROR] Database query failed: {e}")
        return []

# --- CSV Generation ---
def generate_tipsheet_csv(races):
    """Generate CSV tipsheet from qualified races."""
    if not races:
        print("[INFO] No qualified races found.")
        return 0

    with open(CONFIG.OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Track', 'Race #', 'Post Time', 'Score',
            'Trifecta Factors', 'Race ID'
        ])

        for race in races:
            try:
                post_time = datetime.fromisoformat(race['post_time'])
                post_time_str = post_time.strftime('%H:%M')
            except (ValueError, TypeError):
                post_time_str = 'Unknown'

            try:
                factors = json.loads(race['trifecta_factors_json'])
                factors_str = json.dumps(factors, indent=2)
            except (json.JSONDecodeError, TypeError):
                factors_str = race['trifecta_factors_json'] or '{}'

            writer.writerow([
                race['track_name'],
                race['race_number'] or 'N/A',
                post_time_str,
                f"{race['checkmate_score']:.1f}",
                factors_str,
                race['race_id']
            ])

    print(f"[SUCCESS] Tipsheet generated: {CONFIG.OUTPUT_CSV_PATH}")
    print(f"[SUCCESS] {len(races)} qualified races written to CSV")
    return len(races)

# --- Main Orchestrator ---
def run_tipsheet_generation():
    """Main execution flow."""
    print("=" * 70)
    print(f"  Checkmate Tipsheet Generator - {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 70)

    if not ensure_database_exists():
        print("[FATAL] Cannot proceed without database")
        return

    print("\n[INFO] Fetching races from all adapters...")
    orchestrator = DataSourceOrchestrator()
    analyzer = TrifectaAnalyzer()
    settings = Settings()

    all_races, statuses = orchestrator.get_races()
    print(f"[INFO] Fetched {len(all_races)} total races")

    print("[INFO] Analyzing races...")
    analyzed_races = [analyzer.analyze_race(race, settings) for race in all_races]

    qualified_races = [r for r in analyzed_races if r.is_qualified]
    print(f"[INFO] {len(qualified_races)} races qualified")

    print("[INFO] Updating database...")
    with sqlite3.connect(CONFIG.DB_PATH) as conn:
        for race in analyzed_races:
            conn.execute("""
                INSERT OR REPLACE INTO live_races
                (race_id, track_name, race_number, post_time,
                 raw_data_json, checkmate_score, qualified,
                 trifecta_factors_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                race.race_id, race.track_name, race.race_number,
                race.post_time.isoformat() if race.post_time else None,
                race.model_dump_json(), race.checkmate_score,
                race.is_qualified, race.trifecta_factors_json,
                datetime.now().isoformat()
            ))

        for status in statuses:
            conn.execute("""
                INSERT OR REPLACE INTO adapter_status
                (adapter_name, status, last_run, races_found,
                 execution_time_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                status.get('adapter_id'),
                status.get('status'),
                status.get('timestamp').isoformat() if status.get('timestamp') else None,
                status.get('races_found', 0),
                int(status.get('response_time', 0) * 1000),
                status.get('error_message')
            ))

        conn.commit()

    print("[INFO] Database updated successfully")

    print("\n[INFO] Generating CSV tipsheet...")
    qualified_from_db = get_qualified_races_from_db()
    count = generate_tipsheet_csv(qualified_from_db)

    print("\n" + "=" * 70)
    print(f"  Tipsheet generation complete!")
    print(f"  Total races processed: {len(all_races)}")
    print(f"  Qualified races: {count}")
    print(f"  Output: {CONFIG.OUTPUT_CSV_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    run_tipsheet_generation()
