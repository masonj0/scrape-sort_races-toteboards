# run_python_service_demonstration.py
# A temporary script to run the core service logic for demonstration purposes,
# bypassing the Windows-specific service wrapper.

import logging
import os
import sys
from python_service.checkmate_service import CheckmateBackgroundService

# Add the project root to the Python path to ensure correct module resolution
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)


def main():
    """
    Initializes the background service and runs one complete data collection
    and analysis cycle.
    """
    # Configure logging to show timestamps and service names
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger("DemonstrationScript")
    logger.info("Instantiating CheckmateBackgroundService...")

    try:
        service = CheckmateBackgroundService()
        logger.info("Service instantiated. Starting one-shot data collection and analysis cycle.")

        # This is the core logic from inside the service's run_continuously loop
        races, statuses = service.orchestrator.get_races()

        analyzed_races = None
        # This logic correctly tests the Rust engine fallback
        if os.path.exists(service.rust_engine_path):
            logger.info("Rust engine path exists. Attempting to use it.")
            analyzed_races = service._analyze_with_rust(races)

        if analyzed_races is None: # Fallback condition
            logger.info("Rust analysis was not performed or failed. Falling back to Python analyzer.")
            analyzed_races = service._analyze_with_python(races)

        if analyzed_races:
            logger.info(f"Analysis complete. Updating database with {len(analyzed_races)} races.")
            service.db_handler.update_races_and_status(analyzed_races, statuses)
        else:
            logger.warning("No races were analyzed. Database will not be updated.")

        logger.info("Demonstration cycle complete.")

    except Exception as e:
        logging.critical(f"An unhandled exception occurred during the demonstration run: {e}", exc_info=True)

if __name__ == "__main__":
    main()