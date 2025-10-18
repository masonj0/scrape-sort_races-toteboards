import sqlite3
from typing import List
from collections import defaultdict
from paddock_parser.models import Race, Runner, Prediction

class DatabaseManager:
    def __init__(self, db_path: str):
        """Initializes the DatabaseManager and connects to the database."""
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
        self.conn.execute("PRAGMA foreign_keys = 1")

    def create_tables(self):
        """Creates the necessary tables if they don't already exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS races (
                race_id TEXT PRIMARY KEY,
                venue TEXT NOT NULL,
                race_time TEXT NOT NULL,
                race_number INTEGER NOT NULL,
                is_handicap INTEGER NOT NULL,
                source TEXT,
                sources TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runners (
                runner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id TEXT NOT NULL,
                name TEXT NOT NULL,
                odds TEXT NOT NULL,
                is_winner INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (race_id) REFERENCES races (race_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id TEXT NOT NULL,
                track TEXT NOT NULL,
                race_number INTEGER NOT NULL,
                predicted_at TEXT NOT NULL,
                favorite_name TEXT NOT NULL,
                favorite_odds REAL NOT NULL,
                UNIQUE(race_id, predicted_at)
            )
        """)
        self.conn.commit()

    def save_prediction(self, prediction: Prediction):
        """Saves a prediction to the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO predictions (race_id, track, race_number, predicted_at, favorite_name, favorite_odds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                prediction.race_id,
                prediction.track,
                prediction.race_number,
                prediction.predicted_at.isoformat(),
                prediction.favorite_name,
                prediction.favorite_odds
            ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # This is expected if we try to log the same opportunity again, so we can ignore it silently.
            self.conn.rollback()
        except sqlite3.Error as e:
            print(f"Database error during prediction save: {e}")
            self.conn.rollback()

    def save_race(self, race: Race):
        """Saves a race and its runners to the database using an upsert logic."""
        cursor = self.conn.cursor()
        try:
            sources_json = ",".join(race.sources) if race.sources else ""
            cursor.execute("""
                INSERT OR REPLACE INTO races (race_id, venue, race_time, race_number, is_handicap, source, sources)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (race.race_id, race.venue, race.race_time, race.race_number, race.is_handicap, race.source, sources_json))

            cursor.execute("DELETE FROM runners WHERE race_id = ?", (race.race_id,))

            if race.runners:
                runner_data = [(race.race_id, r.name, r.odds, r.is_winner) for r in race.runners]
                cursor.executemany("""
                    INSERT INTO runners (race_id, name, odds, is_winner)
                    VALUES (?, ?, ?, ?)
                """, runner_data)

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()

    def get_all_races(self) -> List[Race]:
        """Retrieves all races and their runners from the database."""
        cursor = self.conn.cursor()

        # Fetch all runners and group them by race_id
        cursor.execute("SELECT * FROM runners")
        runners_by_race = defaultdict(list)
        for row in cursor.fetchall():
            runner = Runner(
                name=row['name'],
                odds=row['odds'],
                is_winner=bool(row['is_winner'])
            )
            runners_by_race[row['race_id']].append(runner)

        # Fetch all races and attach the grouped runners
        cursor.execute("SELECT * FROM races")
        races = []
        for row in cursor.fetchall():
            race_id = row['race_id']
            race = Race(
                race_id=race_id,
                venue=row['venue'],
                race_time=row['race_time'],
                race_number=row['race_number'],
                is_handicap=bool(row['is_handicap']),
                source=row['source'],
                sources=row['sources'].split(',') if row['sources'] else [],
                runners=runners_by_race.get(race_id, [])
            )
            races.append(race)

        return races

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
