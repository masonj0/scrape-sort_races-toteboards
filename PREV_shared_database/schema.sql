-- OPTIMIZED DATABASE SCHEMA FOR HYBRID ARCHITECTURE
CREATE TABLE IF NOT EXISTS live_races (
    race_id TEXT PRIMARY KEY,
    track_name TEXT NOT NULL,
    race_number INTEGER,
    post_time DATETIME NOT NULL,
    raw_data_json TEXT,           -- Complete race data from Python
    checkmate_score REAL NOT NULL,
    qualified BOOLEAN NOT NULL,
    trifecta_factors_json TEXT,   -- Analysis factors for display
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adapter_status (
    adapter_name TEXT PRIMARY KEY,
    status TEXT NOT NULL,         -- 'OK', 'ERROR', 'WARNING'
    last_run DATETIME NOT NULL,
    races_found INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    error_message TEXT,
    success_rate REAL DEFAULT 1.0
);

-- PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_races_qualified_score ON live_races(qualified, checkmate_score DESC, post_time);

-- CLEANUP TRIGGER (AUTOMATIC OLD DATA REMOVAL)
CREATE TRIGGER IF NOT EXISTS cleanup_old_races
AFTER INSERT ON live_races
BEGIN
    DELETE FROM live_races
    WHERE post_time < datetime('now', '-4 hours');
END;

-- Add the qualified_races view that C# and Excel expect
CREATE VIEW IF NOT EXISTS qualified_races AS
SELECT
    race_id,
    track_name,
    race_number,
    post_time,
    checkmate_score,
    qualified,
    trifecta_factors_json
FROM live_races
WHERE qualified = 1
ORDER BY checkmate_score DESC, post_time ASC;