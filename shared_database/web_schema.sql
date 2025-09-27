-- ADD WEB-SPECIFIC TABLES TO EXISTING SCHEMA
CREATE TABLE web_users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE web_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES web_users(user_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);

CREATE TABLE web_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES web_users(user_id),
    race_id TEXT,
    alert_type TEXT, -- 'high_score', 'custom'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);