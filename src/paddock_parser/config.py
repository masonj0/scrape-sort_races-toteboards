# src/paddock_parser/config.py

# --- Filtering Criteria ---

# The minimum number of runners a race must have to be included in the report.
MIN_RUNNERS = 7

# The time window in minutes from now to include races.
# For example, 25 means only show races starting in the next 25 minutes.
TIME_WINDOW_MINUTES = 25

# --- Adapter Configuration ---

# You can disable specific adapters by adding their SOURCE_ID to this list.
# e.g., DISABLED_ADAPTERS = ["skysports", "attheraces"]
DISABLED_ADAPTERS = []

# --- Logging Configuration ---

# Set the log level for the application.
# Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"

# The path to the log file for analysis.
LOG_FILE_PATH = "paddock_parser.log"

# --- Scorer Configuration ---

# Weights for the dynamic scoring engine. These values should ideally sum to 1.0
# but are not required to. Adjust them to prioritize different factors.
SCORER_WEIGHTS = {
    "FIELD_SIZE_WEIGHT": 0.5,      # Prioritizes smaller fields. Score = (1 / number_of_runners) * WEIGHT
    "FAVORITE_ODDS_WEIGHT": 0.3,   # Prioritizes races where the favorite has higher odds. Score = (favorite_odds) * WEIGHT
    "CONTENTION_WEIGHT": 0.2,      # Prioritizes races with low contention (large gap between fav and 2nd fav). Score = (abs(fav_odds - 2nd_fav_odds)) * WEIGHT
}
