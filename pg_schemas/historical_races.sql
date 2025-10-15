-- Schema for the main historical races data warehouse table
CREATE TABLE IF NOT EXISTS historical_races (
    race_id VARCHAR(255) PRIMARY KEY,
    venue VARCHAR(100) NOT NULL,
    race_number INTEGER NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50),
    qualification_score NUMERIC(5, 2),
    field_size INTEGER,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
