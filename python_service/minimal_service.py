# python_service/minimal_service.py
# This is the minimal, sanctioned Flask backend for Checkmate Solo.

import random
from datetime import datetime
from datetime import timedelta

from flask import Flask
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
# This enables CORS for all domains on all routes.
# For a production environment, you would want to restrict this
# to the domain of your frontend application.
CORS(app)


def generate_mock_race(race_id: int):
    """Generates a single mock race with randomized data, mirroring the frontend's mock generator."""
    tracks = ["Belmont Park", "Churchill Downs", "Santa Anita", "Keeneland", "Del Mar"]
    horses = [
        "Thunder Strike",
        "Lightning Bolt",
        "Swift Arrow",
        "Golden Dream",
        "Storm Chaser",
        "Midnight Runner",
        "Royal Flash",
        "Desert Wind",
    ]

    race_horses = []
    for i in range(8):
        betfair = round(2 + random.random() * 15, 2)
        pointsbet = round(betfair * (0.9 + random.random() * 0.2), 2)
        tvg = round(betfair * (0.85 + random.random() * 0.3), 2)

        odds_values = {"Betfair": betfair, "PointsBet": pointsbet, "TVG": tvg}
        best_source = min(odds_values, key=odds_values.get)
        best_odds = odds_values[best_source]

        avg_odds = (betfair + pointsbet + tvg) / 3
        value_score = ((avg_odds - best_odds) / best_odds) * 100 if best_odds > 0 else 0

        race_horses.append(
            {
                "number": i + 1,
                "name": random.choice(horses),
                "odds": {
                    "betfair": f"{betfair:.2f}",
                    "pointsbet": f"{pointsbet:.2f}",
                    "tvg": f"{tvg:.2f}",
                    "best": f"{best_odds:.2f}",
                    "best_source": best_source,
                },
                "value_score": f"{value_score:.1f}",
                "trend": random.choice(["up", "down"]),
            }
        )

    race_horses.sort(key=lambda x: float(x["value_score"]), reverse=True)

    return {
        "id": race_id,
        "track": random.choice(tracks),
        "race_number": random.randint(1, 10),
        "post_time": (datetime.now() + timedelta(minutes=random.randint(5, 120))).isoformat(),
        "horses": race_horses,
    }


@app.route("/api/races/live", methods=["GET"])
def get_live_races():
    """
    This endpoint provides a list of live mock race data for the frontend.
    It mimics the data structure the CheckmateSolo component expects.
    """
    mock_races = [generate_mock_race(i) for i in range(5)]
    return jsonify(mock_races)


if __name__ == "__main__":
    # The frontend component's TODO comment specifies port 8000.
    print("Starting Checkmate Solo minimal backend service...")
    print("API available at http://localhost:8000/api/races/live")
    app.run(host="0.0.0.0", port=8000, debug=False)
