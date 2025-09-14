#!/usr/bin/env python3
"""
Checkmate V3.0: Favorite to Place ROI System - Python Implementation
Translates the HTML/JS horse racing monitoring system to Python
"""

import asyncio
import aiohttp
import json
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue

# --- Configuration ---
CORS_PROXY = "https://proxy.cors.sh/"
UPDATE_INTERVAL = 60  # seconds
FETCH_TIMEOUT = 15    # seconds
MAX_CONCURRENCY = 6
FIXED_STAKE = 10      # dollars
PLACE_PAYOUT_ESTIMATE = 0.6

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Data Classes ---
@dataclass
class Runner:
    name: str
    odds: float

@dataclass
class Race:
    discipline: str
    track: str
    race_number: int
    runners: List[Runner]
    race_time: Optional[str] = None

@dataclass
class PlaceBetAnalysis:
    should_bet: bool
    favorite: Optional[Runner]
    place_probability: float
    expected_value: float
    estimated_place_odds: float
    reason: str

@dataclass
class Prediction:
    race_key: str
    timestamp: str
    track: str
    race_number: int
    favorite: Runner
    field_size: int
    place_probability: float
    expected_value: float
    estimated_place_odds: float
    stake: float
    status: str = 'pending'

@dataclass
class RaceResult:
    race_key: str
    track: str
    race_number: int
    completed: bool
    favorite_finished_in_place: bool
    place_payout: float
    source: str
    fetched_at: str

@dataclass
class AuditRecord:
    prediction: Prediction
    result: RaceResult
    won: bool
    actual_payout: float
    profit: float
    roi: float
    audited_at: str


# --- Database Manager (The Guardian) ---
class DatabaseManager:
    """Handle SQLite database operations"""

    def __init__(self, db_path: str = "checkmate.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    race_key TEXT PRIMARY KEY,
                    timestamp TEXT,
                    track TEXT,
                    race_number INTEGER,
                    favorite_name TEXT,
                    favorite_odds REAL,
                    field_size INTEGER,
                    place_probability REAL,
                    expected_value REAL,
                    estimated_place_odds REAL,
                    stake REAL,
                    status TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_key TEXT,
                    won BOOLEAN,
                    actual_payout REAL,
                    profit REAL,
                    roi REAL,
                    audited_at TEXT,
                    FOREIGN KEY (race_key) REFERENCES predictions (race_key)
                )
            """)

    def save_prediction(self, prediction: Prediction):
        """Save prediction to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.race_key, prediction.timestamp, prediction.track,
                prediction.race_number, prediction.favorite.name, prediction.favorite.odds,
                prediction.field_size, prediction.place_probability, prediction.expected_value,
                prediction.estimated_place_odds, prediction.stake, prediction.status
            ))

    def get_pending_predictions(self) -> List[Prediction]:
        """Get all pending predictions"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM predictions WHERE status = 'pending'").fetchall()
            predictions = []
            for row in rows:
                favorite = Runner(name=row[4], odds=row[5])
                predictions.append(Prediction(
                    race_key=row[0], timestamp=row[1], track=row[2],
                    race_number=row[3], favorite=favorite, field_size=row[6],
                    place_probability=row[7], expected_value=row[8],
                    estimated_place_odds=row[9], stake=row[10], status=row[11]
                ))
            return predictions

    def save_audit_record(self, audit: AuditRecord):
        """Save audit record and update prediction status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE predictions SET status = ? WHERE race_key = ?",
                ('audited', audit.prediction.race_key)
            )
            conn.execute("""
                INSERT INTO audit_records (race_key, won, actual_payout, profit, roi, audited_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                audit.prediction.race_key, audit.won, audit.actual_payout,
                audit.profit, audit.roi, audit.audited_at
            ))

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as total_wins,
                    SUM(profit) as total_profit,
                    SUM(p.stake) as total_staked
                FROM audit_records a
                JOIN predictions p ON a.race_key = p.race_key
            """).fetchone()

            if result and result[0] > 0:
                total_bets, total_wins, total_profit, total_staked = result
                total_bets = total_bets or 0
                total_wins = total_wins or 0
                total_profit = total_profit or 0
                total_staked = total_staked or 0
                return {
                    'total_bets': total_bets,
                    'total_wins': total_wins,
                    'win_rate': (total_wins / total_bets) * 100 if total_bets > 0 else 0,
                    'total_profit': total_profit,
                    'total_staked': total_staked,
                    'roi': (total_profit / total_staked) * 100 if total_staked > 0 else 0
                }
            return {
                'total_bets': 0, 'total_wins': 0, 'win_rate': 0,
                'total_profit': 0, 'total_staked': 0, 'roi': 0
            }

    def clear_all_data(self):
        """Clear all data from predictions and audit_records tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM audit_records")
            conn.execute("DELETE FROM predictions")

# --- Race Data Fetcher (The Template) ---
class RaceDataFetcher:
    """Handle fetching race data from various sources"""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def parse_odds(self, odds_str: str) -> Optional[float]:
        """Parse odds string to float"""
        if not odds_str:
            return None

        s = str(odds_str).strip().upper()
        if not s or s in ['-', '--', 'SCR', 'SCRATCHED']:
            return None
        if 'ML' in s:
            return None
        if s in ['EVS', 'EVEN', 'EVEN MONEY', 'EVEN/MONEY']:
            return 1.0

        if '/' in s:
            parts = s.split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return float(parts[0]) / float(parts[1])

        try:
            return float(s)
        except ValueError:
            return None

    async def fetch_twinspires_data(self) -> List[Race]:
        # This is a placeholder for the actual implementation
        logging.info("Fetching data from TwinSpires...")
        return []

    async def fetch_rpb2b_data(self) -> List[Race]:
        # This is a placeholder for the actual implementation
        logging.info("Fetching data from RPB2B...")
        return []

    def get_test_data(self) -> List[Race]:
        """Generate test data"""
        return [
            Race(
                discipline='Thoroughbred',
                track='Test Park',
                race_number=1,
                race_time='2:15 PM',
                runners=[
                    Runner('Alpha', 1.5), Runner('Bravo', 3.8), Runner('Charlie', 5.0),
                    Runner('Delta', 7.0), Runner('Eagle', 10.0)
                ]
            ),
            Race(
                discipline='Thoroughbred',
                track='Demo Downs',
                race_number=3,
                race_time='3:05 PM',
                runners=[
                    Runner('Echo', 0.8), Runner('Foxtrot', 2.8), Runner('Golf', 9.0)
                ]
            ),
            Race(
                discipline='Thoroughbred',
                track='Sample Stakes',
                race_number=5,
                race_time='4:00 PM',
                runners=[
                    Runner('Hotel', 2.2), Runner('India', 3.5), Runner('Juliet', 4.0),
                    Runner('Kilo', 8.0), Runner('Lima', 12.0), Runner('Mike', 15.0),
                    Runner('November', 20.0), Runner('Oscar', 25.0)
                ]
            )
        ]

# --- Place Bet Analyzer (The Brain) ---
class PlaceBetAnalyzer:
    """Analyze races for place betting opportunities"""

    def identify_favorite(self, runners: List[Runner]) -> Optional[Runner]:
        if not runners:
            return None
        return min(runners, key=lambda r: r.odds)

    def calculate_place_probability(self, favorite: Runner, field_size: int) -> float:
        implied_win_prob = 1 / (favorite.odds + 1)

        if field_size <= 4:
            return implied_win_prob + (1 - implied_win_prob) * 0.6
        elif field_size <= 7: # Standard for 5-7 runners, 2 places
            return implied_win_prob + (1 - implied_win_prob) * 0.5
        else: # Standard for 8+ runners, 3 places
            return implied_win_prob + (1 - implied_win_prob) * 0.4

    def calculate_expected_value(self, favorite: Runner, place_probability: float) -> float:
        estimated_place_odds = favorite.odds * PLACE_PAYOUT_ESTIMATE
        return (place_probability * (1 + estimated_place_odds)) - 1

    def analyze_race(self, race: Race) -> PlaceBetAnalysis:
        if race.discipline != 'Thoroughbred':
            return PlaceBetAnalysis(False, None, 0, 0, 0, 'Not thoroughbred racing')

        runners = [r for r in race.runners if r.odds is not None]
        field_size = len(runners)

        if not (5 <= field_size <= 12):
            return PlaceBetAnalysis(False, None, 0, 0, 0, f'Field size {field_size} outside optimal range (5-12)')

        favorite = self.identify_favorite(runners)
        if not favorite:
            return PlaceBetAnalysis(False, None, 0, 0, 0, 'No clear favorite')

        place_probability = self.calculate_place_probability(favorite, field_size)
        expected_value = self.calculate_expected_value(favorite, place_probability)
        estimated_place_odds = favorite.odds * PLACE_PAYOUT_ESTIMATE

        min_odds, max_odds = (1.4, 4.5) if field_size <= 7 else (1.8, 6.0)

        if not (min_odds <= favorite.odds <= max_odds):
            return PlaceBetAnalysis(False, favorite, place_probability, expected_value, estimated_place_odds, f'Odds ({favorite.odds:.2f}) outside range [{min_odds}, {max_odds}]')

        if place_probability < 0.65:
            return PlaceBetAnalysis(False, favorite, place_probability, expected_value, estimated_place_odds, f'Place probability too low ({place_probability:.2f})')

        if expected_value < 0.05:
            return PlaceBetAnalysis(False, favorite, place_probability, expected_value, estimated_place_odds, f'EV too low ({expected_value:.2f})')

        return PlaceBetAnalysis(True, favorite, place_probability, expected_value, estimated_place_odds, 'Strong place bet opportunity')

# --- Main Application GUI (The Face) ---
class CheckmateGUI:
    """Tkinter GUI for the Checkmate application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Checkmate V3.0: Favorite to Place ROI System")
        self.root.geometry("1200x800")

        self.db_manager = DatabaseManager()
        self.analyzer = PlaceBetAnalyzer()
        self.is_monitoring = False
        self.update_queue = queue.Queue()

        self.setup_ui()
        self.update_performance_display()
        self.root.after(100, self.check_queue)

    def setup_ui(self):
        # Control Frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        self.monitor_btn = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=5)
        self.source_var = tk.StringVar(value="Test Data")
        source_combo = ttk.Combobox(control_frame, textvariable=self.source_var, values=["TwinSpires", "RPB2B", "Test Data"], state="readonly")
        source_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Audit Pending Bets", command=self.audit_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = ttk.Label(self.root, text="Ready to begin.", padding="5")
        self.status_label.pack(fill=tk.X)

        # Performance Frame
        perf_frame = ttk.LabelFrame(self.root, text="Performance Tracker", padding="10")
        perf_frame.pack(fill=tk.X, padx=10)
        self.total_bets_label = ttk.Label(perf_frame, text="Total Bets: 0")
        self.total_bets_label.grid(row=0, column=0, padx=10)
        self.win_rate_label = ttk.Label(perf_frame, text="Win Rate: 0.00%")
        self.win_rate_label.grid(row=0, column=1, padx=10)
        self.net_pl_label = ttk.Label(perf_frame, text="Net P/L: $0.00")
        self.net_pl_label.grid(row=0, column=2, padx=10)
        self.roi_label = ttk.Label(perf_frame, text="ROI: 0.00%")
        self.roi_label.grid(row=0, column=3, padx=10)

        # Notebook for tabs
        notebook = ttk.Notebook(self.root, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True)
        self.opps_tree = self.create_treeview(notebook, 'Betting Opportunities', ('Track', 'Race', 'Favorite', 'Odds', 'PlaceProb', 'EV', 'Stake'))
        self.races_tree = self.create_treeview(notebook, 'All Races', ('Track', 'Race', 'Favorite', 'Odds', 'Field', 'Reason'))

    def create_treeview(self, parent, text, columns):
        frame = ttk.Frame(parent)
        parent.add(frame, text=text)
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.monitor_btn.config(text="Stop Monitoring")
            self.status_label.config(text="Starting monitoring thread...")
            threading.Thread(target=self.monitor_loop, daemon=True).start()
        else:
            self.monitor_btn.config(text="Start Monitoring")
            self.status_label.config(text="Monitoring stopped.")

    def monitor_loop(self):
        while self.is_monitoring:
            self.update_queue.put(('status', 'Fetching race data...'))
            try:
                asyncio.run(self.fetch_and_process_races())
            except Exception as e:
                self.update_queue.put(('error', f"Error in monitor loop: {e}"))
            time.sleep(UPDATE_INTERVAL)

    async def fetch_and_process_races(self):
        fetcher = RaceDataFetcher()
        source = self.source_var.get()
        if source == "Test Data":
            races = fetcher.get_test_data()
        else:
            async with fetcher:
                if source == "TwinSpires":
                    races = await fetcher.fetch_twinspires_data()
                else:
                    races = await fetcher.fetch_rpb2b_data()
        self.update_queue.put(('races', races))

    def check_queue(self):
        try:
            while True:
                msg_type, data = self.update_queue.get_nowait()
                if msg_type == 'status':
                    self.status_label.config(text=data)
                elif msg_type == 'error':
                    self.status_label.config(text=f"ERROR: {data}")
                    messagebox.showerror("Error", data)
                elif msg_type == 'races':
                    self.process_race_data(data)
                    self.status_label.config(text=f"Updated at {datetime.now().strftime('%H:%M:%S')}. Waiting for next cycle...")
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def process_race_data(self, races: List[Race]):
        self.races_tree.delete(*self.races_tree.get_children())
        self.opps_tree.delete(*self.opps_tree.get_children())

        for race in races:
            analysis = self.analyzer.analyze_race(race)
            fav_name = analysis.favorite.name if analysis.favorite else 'N/A'
            fav_odds = f"{analysis.favorite.odds:.2f}" if analysis.favorite else 'N/A'

            self.races_tree.insert('', 'end', values=(
                race.track, f"R{race.race_number}", fav_name, fav_odds,
                len(race.runners), analysis.reason
            ))

            if analysis.should_bet:
                self.opps_tree.insert('', 'end', values=(
                    race.track, f"R{race.race_number}", analysis.favorite.name, f"{analysis.favorite.odds:.2f}",
                    f"{analysis.place_probability:.2%}", f"{analysis.expected_value:.2%}", f"${FIXED_STAKE:.2f}"
                ))
                prediction = Prediction(
                    race_key=f"{race.track}-{race.race_number}-{datetime.now().strftime('%Y%m%d')}",
                    timestamp=datetime.now().isoformat(), track=race.track, race_number=race.race_number,
                    favorite=analysis.favorite, field_size=len(race.runners),
                    place_probability=analysis.place_probability, expected_value=analysis.expected_value,
                    estimated_place_odds=analysis.estimated_place_odds, stake=FIXED_STAKE
                )
                self.db_manager.save_prediction(prediction)

    def audit_results(self):
        # In a real application, this would fetch real results.
        # Here we simulate it for pending bets.
        pending = self.db_manager.get_pending_predictions()
        if not pending:
            messagebox.showinfo("Audit", "No pending bets to audit.")
            return

        for pred in pending:
            # SIMULATION: 50% chance the favorite places
            import random
            won = random.random() < pred.place_probability
            payout = (pred.estimated_place_odds * pred.stake) / 2 if won else 0 # Place pays on half stake
            profit = payout - pred.stake

            result = RaceResult(pred.race_key, pred.track, pred.race_number, True, won, payout, 'simulated', datetime.now().isoformat())
            audit = AuditRecord(pred, result, won, payout, profit, (profit/pred.stake)*100, datetime.now().isoformat())
            self.db_manager.save_audit_record(audit)

        messagebox.showinfo("Audit", f"Audited {len(pending)} pending bets.")
        self.update_performance_display()

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all prediction and audit history?"):
            self.db_manager.clear_all_data()
            self.update_performance_display()
            messagebox.showinfo("Success", "All history has been cleared.")

    def update_performance_display(self):
        stats = self.db_manager.get_performance_stats()
        self.total_bets_label.config(text=f"Total Bets: {stats['total_bets']}")
        self.win_rate_label.config(text=f"Win Rate: {stats['win_rate']:.2f}%")
        self.net_pl_label.config(text=f"Net P/L: ${stats['total_profit']:.2f}")
        self.roi_label.config(text=f"ROI: {stats['roi']:.2f}%")

if __name__ == "__main__":
    app_root = tk.Tk()
    gui = CheckmateGUI(app_root)
    app_root.mainloop()
