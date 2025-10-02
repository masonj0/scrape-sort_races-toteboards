# python_service/api.py

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .engine import CheckmateEngine

# Load environment variables from .env file
load_dotenv()

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Apply CORS settings to allow requests from the frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

engine = CheckmateEngine()

@app.route('/api/odds', methods=['GET'])
def get_odds():
    """New endpoint to fetch formatted odds for the frontend."""
    try:
        results = engine.get_current_odds()
        serializable_results = [r.dict() for r in results]
        return jsonify({"success": True, "data": serializable_results}), 200
    except Exception as e:
        logging.error(f"Error in /api/odds: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/scrape', methods=['GET'])
def scrape():
    """Original endpoint, now used to manually trigger a data refresh."""
    try:
        result = engine.scrape_all()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error in /scrape: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
