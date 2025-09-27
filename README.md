# Checkmate V8: Windows Hybrid Architecture (Hardened)

This project is a high-performance desktop application for real-time horse racing analysis, built on a hardened, reliable hybrid architecture.

## Core Principles

1.  **Reliable Trigger:** Communication between the Python backend and C# frontend is handled via a database `events` table, not an unreliable file watcher.
2.  **Engine Does the Thinking:** The Python service performs all heavy computation (fetching, parsing, scoring). The C# app is a pure, high-speed display client for pre-calculated results.
3.  **Assume Failure:** All components are built with resilience, including database retry logic, full asynchronicity, and structured logging.

## Architecture

- **Python Backend Service:** A silent service for data collection and analysis. It writes fully analyzed results (including scores) to a local SQLite database.
- **C# Desktop Application:** A native Windows app for ultra-fast display of pre-calculated data.

## Database Schema

```sql
CREATE TABLE live_races (
    race_id TEXT PRIMARY KEY,
    track_name TEXT,
    post_time DATETIME,
    source TEXT,
    checkmate_score REAL, -- Pre-calculated by Python
    qualified INTEGER,    -- Pre-calculated by Python
    data_json TEXT,
    updated_at DATETIME
);

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    payload TEXT
);

```