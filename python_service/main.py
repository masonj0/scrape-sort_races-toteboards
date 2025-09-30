import time
import logging
from checkmate_service import CheckmateBackgroundService

def main():
    """
    Main entry point for the Checkmate Python Service executable.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.info("Initializing Checkmate Python Service...")

    try:
        service = CheckmateBackgroundService()
        service.start()
        logger.info("Service started successfully. Running indefinitely...")

        # Keep the main thread alive to allow the background service to run.
        while True:
            time.sleep(3600)  # Sleep for an hour at a time.

    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
    except Exception as e:
        logger.critical(f"A fatal error occurred: {e}", exc_info=True)
    finally:
        logger.info("Checkmate Python Service is shutting down.")

if __name__ == "__main__":
    main()