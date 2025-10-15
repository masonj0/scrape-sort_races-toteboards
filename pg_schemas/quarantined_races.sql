-- Schema for storing race data that fails validation
CREATE TABLE IF NOT EXISTS quarantined_races (
    quarantine_id SERIAL PRIMARY KEY,
    race_id VARCHAR(255),
    source VARCHAR(50),
    payload JSONB NOT NULL,
    reason VARCHAR(255) NOT NULL,
    quarantined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
