# ==============================================================================
# == Checkmate V8 - Operation: TipSheet
# ==============================================================================
# This script is a simplified, robust, standalone tipsheet generator.
# It embodies the core logic of the Penta-Hybrid system in a single file.
# ==============================================================================

import time
import sqlite3
import json
import csv
import requests
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from functools import wraps

# --- Fortified Settings & Configuration ---
class Config:
    DB_PATH: str = "checkmate_tipsheet.db"
    QUALIFICATION_SCORE: float = 75.0
    FIELD_SIZE_MIN: int = 4
    FIELD_SIZE_MAX: int = 8
    FAVORITE_ODDS_MAX: float = 3.5
    FETCH_TIMEOUT: int = 20
    USER_AGENT: str = "Checkmate/8.0 (TipsheetGenerator)"

CONFIG = Config()

# --- Battle-Tested Resilience Pattern (from Claude/Our Own History) ---
def retry_on_failure(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"[WARN] Attempt {attempt + 1} for {func.__name__} failed: {e}")
                    if attempt == max_retries - 1:
                        return []
                    time.sleep(1 * (2 ** attempt)) # Exponential backoff
            return []
        return decorator
    return decorator

# --- Data Models ---
class Runner(BaseModel):
    name: str
    odds: Optional[float] = None

class RaceCard(BaseModel):
    race_id: str; track_name: str; race_number: int
    post_time: datetime; runners: List[Runner]; source: str

class ScoredRace(RaceCard):
    checkmate_score: float; is_qualified: bool; trifecta_factors: dict

# --- Database Setup ---
def setup_database():
    conn = sqlite3.connect(CONFIG.DB_PATH)
    # (Implementation for table creation as defined in the proposal)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tipsheet_runs (run_id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, races_fetched INTEGER, tipsheet_count INTEGER);
        CREATE TABLE IF NOT EXISTS race_tipsheet (race_id TEXT PRIMARY KEY, track_name TEXT, race_number INTEGER, post_time DATETIME, checkmate_score REAL, factors_json TEXT, source TEXT);
    """)
    conn.commit()
    return conn

# --- Fortified Adapters ---
def parse_odds_robust(odds_input: any) -> Optional[float]:
    """Parses fractional, decimal, and American odds."""
    if not odds_input: return None
    odds_str = str(odds_input).strip()
    try:
        if odds_str.startswith(('+', '-')):
            american = int(odds_str)
            return (american / 100) + 1 if american > 0 else (100 / abs(american)) + 1
        if '/' in odds_str:
            num, den = map(float, odds_str.split('/'))
            return (num / den) + 1.0
        return float(odds_str)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

@retry_on_failure()
def fetch_from_tvg() -> List[RaceCard]:
    """ NOTE: This is a placeholder. The real TVG adapter uses BeautifulSoup. """
    print("[INFO] Fetching from TVG (placeholder)...")
    # In a real scenario, this would use BeautifulSoup to parse tvg.com/tracks
    return []

def get_all_races() -> List[RaceCard]:
    """Orchestrates fetching from all adapters."""
    races = []
    races.extend(fetch_from_tvg())
    # Future adapters would be added here
    print(f"[INFO] Fetched a total of {len(races)} races.")
    return races

# --- Core Logic (Filter & Score) ---
def filter_and_score_races(races: List[RaceCard]) -> List[ScoredRace]:
    """Applies filters and Checkmate scoring logic."""
    scored_races = []
    for race in races:
        runners_with_odds = [r for r in race.runners if r.odds is not None]
        if not (CONFIG.FIELD_SIZE_MIN <= len(runners_with_odds) <= CONFIG.FIELD_SIZE_MAX):
            continue

        odds_list = sorted([r.odds for r in runners_with_odds])
        if not odds_list or odds_list[0] > CONFIG.FAVORITE_ODDS_MAX:
            continue

        # Scoring
        score, factors = 0.0, {}
        if len(runners_with_odds) >= 6: score += 30; factors['field_size'] = 30
        if odds_list[0] <= 2.5: score += 40; factors['strong_fav'] = 40
        if len(odds_list) >= 2 and (odds_list[1] - odds_list[0]) > 2.0: score += 30; factors['odds_spread'] = 30

        is_qualified = score >= CONFIG.QUALIFICATION_SCORE
        scored_races.append(ScoredRace(
            **race.dict(),
            checkmate_score=score,
            is_qualified=is_qualified,
            trifecta_factors=factors
        ))
    print(f"[INFO] {len(scored_races)} races passed filtering and scoring.")
    return scored_races

# --- Output Generation ---
def generate_tipsheet(scored_races: List[ScoredRace], conn):
    qualified = [r for r in scored_races if r.is_qualified]
    print(f"[INFO] {len(qualified)} races are qualified for the tipsheet.")
    if not qualified: return

    # Save to DB
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR REPLACE INTO race_tipsheet VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(r.race_id, r.track_name, r.race_number, r.post_time, r.checkmate_score, json.dumps(r.trifecta_factors), r.source) for r in qualified]
    )

    # Export to CSV
    with open('race_tipsheet.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Race ID', 'Track', 'Race #', 'Post Time', 'Score', 'Factors'])
        for r in qualified:
            writer.writerow([r.race_id, r.track_name, r.race_number, r.post_time.strftime('%H:%M'), r.checkmate_score, json.dumps(r.trifecta_factors)])
    print("[SUCCESS] 'race_tipsheet.csv' has been generated.")

# --- Main Orchestrator ---
def run_tipsheet_cycle():
    """Main execution function."""
    print("\n" + "="*50)
    print(f"  Checkmate Tipsheet Generator - Run at {datetime.now()}")
    print("="*50)

    conn = setup_database()

    all_races = get_all_races()
    scored_races = filter_and_score_races(all_races)
    generate_tipsheet(scored_races, conn)

    # Log run
    conn.execute("INSERT INTO tipsheet_runs (races_fetched, tipsheet_count) VALUES (?, ?)",
                 (len(all_races), len([r for r in scored_races if r.is_qualified])))
    conn.commit()
    conn.close()
    print("[INFO] Cycle complete. Database updated.")

if __name__ == "__main__":
    run_tipsheet_cycle()