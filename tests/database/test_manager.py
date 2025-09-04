import sqlite3
import pytest
from dataclasses import dataclass, field
from typing import List

# Import the data models from their new, dedicated file
from paddock_parser.models import Race, Runner

# This is the class Jules will need to implement in src/paddock_parser/database/manager.py
# The test is written as if this class already exists.
from paddock_parser.database.manager import DatabaseManager

@pytest.fixture
def db_manager():
    """ Fixture to set up an in-memory SQLite database for each test. """
    manager = DatabaseManager(db_path=":memory:")
    yield manager
    manager.close()

@pytest.fixture
def sample_race():
    """ Fixture to provide a sample Race object for testing. """
    return Race(
        race_id="2025-09-03_Aintree_1",
        venue="Aintree",
        race_time="14:30",
        race_number=1,
        is_handicap=True,
        runners=[
            Runner(name="Horse A", odds="10/1"),
            Runner(name="Horse B", odds="5/2"),
        ]
    )

def test_database_manager_initialization(db_manager):
    """ SPEC: The DatabaseManager should initialize a connection to the database. """
    assert db_manager.conn is not None
    assert isinstance(db_manager.conn, sqlite3.Connection)

def test_create_tables(db_manager):
    """ SPEC: The create_tables method should create the 'races' and 'runners' tables. """
    db_manager.create_tables()
    cursor = db_manager.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='races';")
    assert cursor.fetchone() is not None, "The 'races' table was not created."
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runners';")
    assert cursor.fetchone() is not None, "The 'runners' table was not created."

def test_save_race_inserts_new_data(db_manager, sample_race):
    """ SPEC: The save_race method should insert a new race and its runners into the database. """
    db_manager.create_tables()
    db_manager.save_race(sample_race)

    # Verify the race was inserted
    cursor = db_manager.conn.cursor()
    cursor.execute("SELECT venue, race_time, is_handicap FROM races WHERE race_id=?", (sample_race.race_id,))
    race_data = cursor.fetchone()
    assert race_data is not None
    assert tuple(race_data) == ("Aintree", "14:30", 1)

    # Verify the runners were inserted
    cursor.execute("SELECT name, odds FROM runners WHERE race_id=?", (sample_race.race_id,))
    runners_data = cursor.fetchall()
    runners_as_tuples = [tuple(row) for row in runners_data]
    assert len(runners_as_tuples) == 2
    assert ("Horse A", "10/1") in runners_as_tuples
    assert ("Horse B", "5/2") in runners_as_tuples

def test_save_race_is_idempotent_and_updates(db_manager, sample_race):
    """
    SPEC: The save_race method should be an "upsert."
    - It should NOT create duplicate rows for the same race.
    - It SHOULD update the race and runner details if they change.
    """
    db_manager.create_tables()
    # First save
    db_manager.save_race(sample_race)

    # Modify the race details
    updated_race = Race(
        race_id="2025-09-03_Aintree_1", # Same ID
        venue="Aintree",
        race_time="14:35", # Updated time
        race_number=1, # Same race number
        is_handicap=False, # Updated handicap status
        runners=[
            Runner(name="Horse A", odds="12/1"), # Updated odds
            Runner(name="Horse C", odds="8/1"), # New runner
        ]
    )
    # Second save
    db_manager.save_race(updated_race)

    cursor = db_manager.conn.cursor()

    # Verify there is still only ONE race with this ID
    cursor.execute("SELECT COUNT(*) FROM races WHERE race_id=?", (sample_race.race_id,))
    assert cursor.fetchone()[0] == 1, "save_race created a duplicate race."

    # Verify the race details were UPDATED
    cursor.execute("SELECT race_time, is_handicap FROM races WHERE race_id=?", (sample_race.race_id,))
    race_data = cursor.fetchone()
    assert tuple(race_data) == ("14:35", 0)

    # Verify the runners were UPDATED (old ones removed, new ones added)
    cursor.execute("SELECT name, odds FROM runners WHERE race_id=?", (sample_race.race_id,))
    runners_data = cursor.fetchall()
    runners_as_tuples = [tuple(row) for row in runners_data]
    assert len(runners_as_tuples) == 2
    assert ("Horse A", "12/1") in runners_as_tuples
    assert ("Horse C", "8/1") in runners_as_tuples
    assert ("Horse B", "5/2") not in runners_as_tuples
