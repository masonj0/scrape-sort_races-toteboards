CREATE TABLE IF NOT EXISTS quarantine_races (
    quarantine_id SERIAL PRIMARY KEY,
    race_id VARCHAR(100),
    track_name VARCHAR(100),
    race_number INT,
    post_time TIMESTAMP WITH TIME ZONE,
    source VARCHAR(50),
    raw_data_json JSONB, -- Store the original raw data for inspection
    quarantine_reason TEXT, -- Reason for failing validation
    collection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);