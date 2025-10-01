# python_service/api.py
# ==============================================================================
# Checkmate Ultimate - The Full-Power Python Backend API (CORS CORRECTED)
# ==============================================================================

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from engine import DataSourceOrchestrator, TrifectaAnalyzer, Settings

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

orchestrator = DataSourceOrchestrator()
analyzer = TrifectaAnalyzer()
settings = Settings()

logging.info("Checkmate Ultimate Backend initialized with CORS enabled.")

@app.route('/api/races/live', methods=['GET'])
def get_live_races():
    logging.info("Request received for /api/races/live")
    try:
        all_races, _ = orchestrator.get_races()
        analyzed_races = [analyzer.analyze_race(race, settings) for race in all_races]
        races_dict = [race.model_dump() for race in analyzed_races]
        return jsonify(races_dict)
    except Exception as e:
        logging.critical(f"FATAL error in get_live_races: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    from waitress import serve
    print("\n" + "="*60)
    print("  STARTING CHECKMATE ULTIMATE BACKEND (FULL POWER)")
    print("  Listening on http://localhost:8000")
    print("="*60 + "\n")
    serve(app, host="0.0.0.0", port=8000)