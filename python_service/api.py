# python_service/api.py

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .engine import EngineManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Whitelist origins for security
CORS(app, origins=["http://localhost:3000", "http://localhost:8000"])

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

engine = EngineManager()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/races', methods=['GET'])
@limiter.limit("10 per minute")
def get_races():
    try:
        races = engine.fetch_and_process_races()
        return jsonify(races), 200
    except Exception as e:
        logging.error(f"Error in /api/races: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/funnel', methods=['GET'])
@limiter.limit("30 per minute")
def get_funnel_stats():
    try:
        stats = engine.get_funnel_statistics()
        return jsonify(stats), 200
    except Exception as e:
        logging.error(f"Error in /api/funnel: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
@limiter.limit("30 per minute")
def get_dashboard_summary():
    """Provides a high-level summary of the last data scrape, including failures."""
    try:
        summary = engine.get_dashboard_summary()
        return jsonify(summary), 200
    except Exception as e:
        logging.error(f"Error in /api/dashboard: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/adapters/<adapter_name>/status', methods=['GET'])
def get_adapter_status(adapter_name):
    status = engine.get_adapter_status(adapter_name)
    if status:
        return jsonify(status), 200
    return jsonify({"error": "Adapter not found"}), 404

# Add other endpoints as needed, applying rate limits where appropriate

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)