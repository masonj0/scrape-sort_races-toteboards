import pytest
import os
import sqlite3
import tkinter as tk
from golden_script.checkmate_python import Race, Runner, PlaceBetAnalyzer, DatabaseManager, Prediction, CheckmateGUI

# --- Fixtures ---
@pytest.fixture
def analyzer():
    return PlaceBetAnalyzer()

@pytest.fixture
def db_manager():
    return DatabaseManager(db_path="file::memory:?cache=shared")

@pytest.fixture
def test_races():
    """Provides a standard set of races for testing."""
    return [
        Race('Thoroughbred', 'Test Park', 1, runners=[
            Runner('Fav', 2.0), Runner('Mid', 5.0), Runner('Long', 10.0), Runner('Extra', 12.0), Runner('Another', 15.0)
        ]),
        Race('Thoroughbred', 'Demo Downs', 3, runners=[
            Runner('TooShort', 0.8), Runner('RunnerUp', 2.8), Runner('Outsider', 9.0)
        ])
    ]

# --- Logic Tests ---
def test_analysis_strong_opportunity(analyzer):
    race = Race('Thoroughbred', 'Test Park', 1, runners=[
        Runner('Fav', 2.0), Runner('Mid', 5.0), Runner('Long', 10.0), Runner('Extra', 12.0), Runner('Another', 15.0)
    ])
    analysis = analyzer.analyze_race(race)
    assert analysis.should_bet is True

def test_db_save_and_get_prediction(db_manager):
    pred = Prediction(
        race_key="Test-1-20250101", timestamp="ts", track="Test", race_number=1,
        favorite=Runner(name="TestHorse", odds=2.5), field_size=8, place_probability=0.7,
        expected_value=0.1, estimated_place_odds=1.5, stake=10.0, status='pending'
    )
    db_manager.save_prediction(pred)
    pending_preds = db_manager.get_pending_predictions()
    assert len(pending_preds) == 1
    assert pending_preds[0].race_key == "Test-1-20250101"

# --- NEW: Logging Verification Test ---
def test_logging_output_during_processing(caplog, test_races, db_manager, analyzer):
    """Verify that correct log messages are emitted during race processing."""
    # Minimal Tkinter setup to avoid running mainloop
    root = tk.Tk()
    gui = CheckmateGUI(root)
    gui.db_manager = db_manager # Substitute in-memory db
    gui.analyzer = analyzer
    root.withdraw() # Hide the GUI window during tests

    with caplog.at_level('INFO'):
        gui.process_race_data(test_races)

    assert "Processing 2 fetched races." in caplog.text
    assert "Saving prediction for race: Test Park-1-" in caplog.text
    assert "Processing complete. Identified 1 new opportunities." in caplog.text
    # Clean up the Tkinter instance
    root.destroy()
