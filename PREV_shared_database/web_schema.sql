-- ADD WEB-SPECIFIC TABLES TO EXISTING SCHEMA
CREATE TABLE IF NOT EXISTS web_users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS web_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES web_users(user_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);

CREATE TABLE IF NOT EXISTS web_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES web_users(user_id),
    race_id TEXT,
    alert_type TEXT, -- 'high_score', 'custom'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- RELIABLE TRIGGER TABLE FOR REAL-TIME WEB UPDATES
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    payload TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);