from src.checkmate_v7.models import HorseSchema, RaceDataSchema, PerformanceMetricsSchema

def test_horse_schema():
    """Tests that the HorseSchema can be instantiated correctly."""
    horse_data = {
        "id": "1",
        "name": "Speedy",
        "number": 1,
        "jockey": "J. Doe",
        "trainer": "T. Smith",
        "odds": 5.0,
        "morningLine": 4.0,
        "speed": 90,
        "class_rating": 95,
        "form": "1-2-3",
        "lastRaced": "10 days ago"
    }
    horse = HorseSchema(**horse_data)
    assert horse.name == "Speedy"
    assert horse.class_rating == 95

def test_race_data_schema():
    """Tests that the RaceDataSchema can be instantiated with nested models."""
    race_data = {
        "id": "R1",
        "track": "Santa Anita",
        "raceNumber": 1,
        "postTime": "2025-09-18T14:00:00Z",
        "horses": [{
            "id": "1", "name": "Speedy", "number": 1, "jockey": "J. Doe",
            "trainer": "T. Smith", "odds": 5.0, "morningLine": 4.0,
            "speed": 90, "class_rating": 95, "form": "1-2-3", "lastRaced": "10 days ago"
        }],
        "conditions": "Clear",
        "distance": "6f",
        "surface": "Dirt",
        "checkmateScore": 8.5,
        "qualified": True,
        "trifectaFactors": {
            "speedAdvantage": True,
            "classEdge": True,
            "valueOdds": False
        }
    }
    race = RaceDataSchema(**race_data)
    assert race.track == "Santa Anita"
    assert len(race.horses) == 1
    assert race.horses[0].name == "Speedy"
    assert race.trifectaFactors.speedAdvantage is True

def test_performance_metrics_schema():
    """Tests that the new PerformanceMetricsSchema can be instantiated."""
    metrics_data = {
        "totalBets": 100,
        "wins": 20,
        "winRate": 20.0,
        "roi": 15.5,
        "profit": 1550.0,
        "confidenceInterval": [10.0, 21.0],
        "sampleSize": 100
    }
    metrics = PerformanceMetricsSchema(**metrics_data)
    assert metrics.totalBets == 100
    assert metrics.roi == 15.5
