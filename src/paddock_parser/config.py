# src/paddock_parser/config.py

# --- Filtering Criteria ---

# The minimum number of runners a race must have to be included in the report.
MIN_RUNNERS = 7

# The time window in minutes from now to include races.
# For example, 25 means only show races starting in the next 25 minutes.
TIME_WINDOW_MINUTES = 115

# --- Adapter Configuration ---

# You can disable specific adapters by adding their SOURCE_ID to this list.
# e.g., DISABLED_ADAPTERS = ["skysports", "attheraces"]
DISABLED_ADAPTERS = []

# --- Logging Configuration ---

# Set the log level for the application.
# Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"

# --- High Roller Report Configuration ---
HIGH_ROLLER_MAX_RUNNERS = 7
HIGH_ROLLER_MIN_ODDS = 0.5
