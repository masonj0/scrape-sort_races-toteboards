import logging
from pythonjsonlogger import jsonlogger
from . import config

def setup_logging():
    """Sets up structured JSON logging for the application."""
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
