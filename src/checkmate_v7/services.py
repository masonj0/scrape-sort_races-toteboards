"""
Checkmate V7: `services.py` - THE GATEWAY
"""
import logging

def process_race_for_prediction(race_url: str):
    """Placeholder for the Celery task to process a race."""
    logging.info(f"SERVICE TASK: Processing {race_url} for prediction.")
    # In a real implementation, this would involve:
    # 1. Calling a DefensiveFetcher to get raw data.
    # 2. Calling a parser to normalize the data.
    # 3. Calling the logic.py functions to score and qualify.
    # 4. Saving the Prediction to the database.
    pass

def process_race_for_results(race_key: str):
    """Placeholder for the Celery task to fetch results."""
    logging.info(f"SERVICE TASK: Fetching results for {race_key}.")
    # 1. Call results adapter.
    # 2. Save Result to database.
    # 3. Trigger Accountant.
    pass
