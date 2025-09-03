import sqlite3
from src.paddock_parser.models import Race

class DatabaseManager:
    def __init__(self, db_path: str):
        """Initializes the DatabaseManager and connects to the database."""
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = 1") # Enforce foreign key constraints

    def create_tables(self):
        """Creates the necessary tables if they don't already exist."""
        cursor = self.conn.cursor()
        # Create races table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS races (
                race_id TEXT PRIMARY KEY,
                venue TEXT NOT NULL,
                race_time TEXT NOT NULL,
                is_handicap INTEGER NOT NULL
            )
        """)
        # Create runners table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runners (
                runner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id TEXT NOT NULL,
                name TEXT NOT NULL,
                odds TEXT NOT NULL,
                FOREIGN KEY (race_id) REFERENCES races (race_id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def save_race(self, race: Race):
        """
        Saves a race and its runners to the database.
        Uses an "upsert" logic: inserts a new race or updates an existing one.
        When a race is updated, its associated runners are replaced.
        """
        cursor = self.conn.cursor()

        # Use a transaction to ensure atomicity
        try:
            # Upsert the race details.
            # The INTEGER type for is_handicap is handled by sqlite3 library bool conversion.
            cursor.execute("""
                INSERT OR REPLACE INTO races (race_id, venue, race_time, is_handicap)
                VALUES (?, ?, ?, ?)
            """, (race.race_id, race.venue, race.race_time, race.is_handicap))

            # Delete old runners for this race to ensure a clean slate before adding new ones.
            # ON DELETE CASCADE on the foreign key would also handle this if we deleted the race,
            # but since we are replacing, an explicit DELETE is clearer and safer.
            cursor.execute("DELETE FROM runners WHERE race_id = ?", (race.race_id,))

            # Insert the new list of runners
            if race.runners:
                runner_data = [(race.race_id, r.name, r.odds) for r in race.runners]
                cursor.executemany("""
                    INSERT INTO runners (race_id, name, odds)
                    VALUES (?, ?, ?)
                """, runner_data)

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()


    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
