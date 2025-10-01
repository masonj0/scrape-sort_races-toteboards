# python_service/main.py
# ==============================================================================
# Checkmate Ultimate Solo - Fortified Python Backend
# ==============================================================================

from flask import Flask, jsonify
from flask_cors import CORS
from engine import DataSourceOrchestrator, TrifectaAnalyzer, Settings
import logging

# --- Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for the React frontend

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# Initialize our battle-tested CORE components
orchestrator = DataSourceOrchestrator()
analyzer = TrifectaAnalyzer()
settings = Settings()

# --- API Endpoints ---
@app.route('/api/races/live', methods=['GET'])
def get_live_races():
    """Fetches, analyzes, and returns live race data in the format expected by the Ultimate frontend."""
    logging.info("Request received for /api/races/live")
    try:
        all_races, _ = orchestrator.get_races()
        analyzed_races = [analyzer.analyze_race(race, settings) for race in all_races]
        races_dict = [race.model_dump() for race in analyzed_races]
        logging.info(f"Successfully processed and returning {len(races_dict)} races.")
        return jsonify(races_dict)
    except Exception as e:
        logging.critical(f"FATAL error in get_live_races: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Provides a basic health check."""
    return jsonify({'status': 'healthy'})

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Checkmate Ultimate Solo Backend on http://localhost:8000")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)