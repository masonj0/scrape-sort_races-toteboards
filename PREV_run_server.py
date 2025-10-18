# run_server.py
# This script serves as the main entrypoint for the Checkmate backend.
# It correctly imports the Flask 'app' object from the 'python_service' package
# and runs it, ensuring that relative imports within the package work as expected.

import os
from python_service.api import app

if __name__ == "__main__":
    # Use the PORT environment variable if available, otherwise default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)