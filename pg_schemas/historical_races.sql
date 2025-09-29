CREATE TABLE IF NOT EXISTS historical_races (
    race_id VARCHAR(100) PRIMARY KEY,
    track_name VARCHAR(100) NOT NULL,
    race_number INT NOT NULL,
    post_time TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50),
    distance_meters INT,
    race_class VARCHAR(100),
    track_condition VARCHAR(50),
    weather VARCHAR(100),
    runners_data JSONB, -- Store the full runner list as a JSON object
    checkmate_score FLOAT,
    is_qualified BOOLEAN,
    collection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    manual_override_by VARCHAR(100) DEFAULT NULL -- Tracks human intervention
);