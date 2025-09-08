# src/paddock_parser/config.py

# --- Filtering Criteria ---
# The minimum number of runners a race must have to be included in the report.
MIN_RUNNERS = 7
# The time window in minutes from now to include races.
TIME_WINDOW_MINUTES = 25

# --- Adapter Configuration ---
# You can disable specific adapters by adding their SOURCE_ID to this list.
DISABLED_ADAPTERS = []

# --- Logging Configuration ---
# Set the log level for the application.
LOG_LEVEL = "INFO"
# The path to the log file for analysis.
LOG_FILE_PATH = "paddock_parser.log"

# --- High Roller Configuration ---
# Used by the legacy get_high_roller_races function.
HIGH_ROLLER_MAX_RUNNERS = 6
HIGH_ROLLER_MIN_ODDS = 3.0

# --- Scorer Configuration ---
# Weights for the dynamic scoring engine.
SCORER_WEIGHTS = {
    "FIELD_SIZE_WEIGHT": 0.5,
    "FAVORITE_ODDS_WEIGHT": 0.3,
    "CONTENTION_WEIGHT": 0.2,

}
