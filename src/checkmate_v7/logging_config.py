import logging
import sys
from pythonjsonlogger import jsonlogger
from . import config

def setup_logging():
    """Sets up structured JSON logging for the application."""
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # Remove any existing handlers to avoid conflicts
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a handler that outputs to stdout
    log_handler = logging.StreamHandler(sys.stdout)

    # Use a JSON formatter, renaming asctime to timestamp to match directive examples
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(name)s %(levelname)s %(message)s',
        rename_fields={'asctime': 'timestamp'}
    )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
