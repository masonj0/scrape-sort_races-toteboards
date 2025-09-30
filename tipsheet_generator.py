# ==============================================================================
# == Checkmate V8 - Tipsheet Generator (PRODUCTION FINAL)
# ==============================================================================
# This is the final, superior architecture for the Tipsheet Generator,
# validated by external AI review for robustness and production readiness.
# ==============================================================================

import csv
import json
import sqlite3
import time
from datetime import datetime
from functools import wraps
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

# --- 1. Fortified Settings & Configuration ---
class Config:
    """Centralized configuration for the generator."""
    # Renamed DB_PATH to reflect the delivered asset name
    DB_PATH: str = "tipsheet_generator.db"
    OUTPUT_CSV_PATH: str = "race_tipsheet.csv" # Renamed CSV to match the original generator's output
    QUALIFICATION_SCORE: float = 75.0
    FIELD_SIZE_MIN: int = 4 # Relaxed field size for more opportunities
    FIELD_SIZE_MAX: int = 8
    FAVORITE_ODDS_MAX: float = 3.5
    ODDS_SPREAD_MIN: float = 2.0
    FETCH_TIMEOUT: int = 20
    USER_AGENT: str = "Checkmate/8.2 (TipsheetGenerator)"

CONFIG = Config()

# --- 2. Battle-Tested Resilience Pattern ---
def retry_on_failure(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    print(f"[WARN] Attempt {attempt + 1} for {func.__name__} failed: {e}")
                    if attempt == max_retries - 1: return []
                    time.sleep(1 * (2 ** attempt))
            return []
        return wrapper
    return decorator

# --- 3. Pydantic Data Models ---
class Runner(BaseModel): name: str; odds: Optional[float] = None
class RaceCard(BaseModel): race_id: str; track_name: str; race_number: int; post_time: datetime; runners: List[Runner]; source: str
class ScoredRace(RaceCard): checkmate_score: float; is_qualified: bool; trifecta_factors: dict

# --- 4. Core Logic & Pipeline ---
def setup_database():
    with sqlite3.connect(CONFIG.DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tipsheet (race_id TEXT PRIMARY KEY, track_name TEXT, race_number INTEGER, post_time TEXT, score REAL, factors TEXT, fetched_at TEXT);
            CREATE TABLE IF NOT EXISTS runs (run_id INTEGER PRIMARY KEY, timestamp TEXT, races_fetched INTEGER, races_qualified INTEGER);
        """)
    print(f"[INFO] Database '{CONFIG.DB_PATH}' is ready.")

def parse_odds_robust(odds_input: any) -> Optional[float]:
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
    except (ValueError, TypeError, ZeroDivisionError): return None

@retry_on_failure()
def fetch_tvg_races() -> List[RaceCard]:
    """Fetches races from the TVG JSON API."""
    print("[INFO] Fetching from TVG...")
    url = "https://mobile-api.tvg.com/api/mobile/races/today"
    response = requests.get(url, headers={'User-Agent': CONFIG.USER_AGENT}, timeout=CONFIG.FETCH_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    races = []
    for race_data in data.get('races', []):
        try:
            runners = [Runner(name=r.get('horseName', 'Unknown'), odds=parse_odds_robust(r.get('odds', {}).get('morningLine'))) for r in race_data.get('runners', []) if not r.get('scratched')]
            races.append(RaceCard(
                race_id=f"tvg_{race_data['id']}", track_name=race_data.get('trackName', 'TVG Track'),
                race_number=race_data.get('raceNumber', 0), post_time=datetime.fromisoformat(race_data.get('postTime')),
                runners=runners, source='TVG'
            ))
        except Exception: continue
    print(f"[INFO] Successfully parsed {len(races)} races from TVG.")
    return races

def get_all_races() -> List[RaceCard]:
    races = []; races.extend(fetch_tvg_races()); return races

def filter_and_score_races(races: List[RaceCard]) -> List[ScoredRace]:
    scored_races = []
    for race in races:
        runners_with_odds = sorted([r for r in race.runners if r.odds is not None], key=lambda r: r.odds)
        if not (CONFIG.FIELD_SIZE_MIN <= len(runners_with_odds) <= CONFIG.FIELD_SIZE_MAX): continue
        if not runners_with_odds or runners_with_odds[0].odds > CONFIG.FAVORITE_ODDS_MAX: continue
        if len(runners_with_odds) < 2 or (runners_with_odds[1].odds - runners_with_odds[0].odds) < CONFIG.ODDS_SPREAD_MIN: continue
        score, factors = 0.0, {}
        if 6 <= len(runners_with_odds) <= 8: score += 40; factors['field_size'] = 40
        if runners_with_odds[0].odds <= 2.5: score += 35; factors['strong_fav'] = 35
        if (runners_with_odds[1].odds - runners_with_odds[0].odds) > 2.5: score += 25; factors['odds_spread'] = 25
        scored_races.append(ScoredRace(**race.dict(), checkmate_score=score, is_qualified=score >= CONFIG.QUALIFICATION_SCORE, trifecta_factors=factors))
    return scored_races

def generate_output(scored_races: List[ScoredRace]):
    qualified_races = [r for r in scored_races if r.is_qualified]
    if not qualified_races: print("[INFO] No races met the qualification score."); return 0
    with sqlite3.connect(CONFIG.DB_PATH) as conn:
        conn.executemany("INSERT OR REPLACE INTO tipsheet VALUES (?, ?, ?, ?, ?, ?, ?)", [(r.race_id, r.track_name, r.race_number, r.post_time.isoformat(), r.checkmate_score, json.dumps(r.trifecta_factors), datetime.now().isoformat()) for r in qualified_races])
    with open(CONFIG.OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f); writer.writerow(['Track', 'Race #', 'Post Time', 'Score', 'Factors', 'Race ID'])
        for r in qualified_races: writer.writerow([r.track_name, r.race_number, r.post_time.strftime('%H:%M'), r.checkmate_score, json.dumps(r.trifecta_factors), r.race_id])
    print(f"[SUCCESS] '{CONFIG.OUTPUT_CSV_PATH}' has been generated with {len(qualified_races)} qualified races.")
    return len(qualified_races)

# --- 5. Main Orchestrator ---
def run_cycle():
    print(f"\\n{'='*60}\\n  Checkmate Tipsheet Generator - Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n{'='*60}")
    setup_database()
    all_races = get_all_races()
    scored_races = filter_and_score_races(all_races)
    qualified_count = generate_output(scored_races)
    with sqlite3.connect(CONFIG.DB_PATH) as conn:
        conn.execute("INSERT INTO runs (timestamp, races_fetched, races_qualified) VALUES (?, ?, ?)", (datetime.now().isoformat(), len(all_races), qualified_count))
    print("[INFO] Cycle complete. Database and CSV updated.")

if __name__ == "__main__":
    run_cycle()
