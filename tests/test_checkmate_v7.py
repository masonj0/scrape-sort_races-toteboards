import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

# Need to ensure the app is imported after the models are defined
# This is brittle, but necessary in this recreation context
from src.checkmate_v7.api import app
from src.checkmate_v7.models import PredictionORM

client = TestClient(app)

@patch('src.checkmate_v7.api.get_db_session')
def test_get_active_predictions(mock_get_db):
    """
    Tests the /predictions/active endpoint, ensuring it correctly calculates
    and returns the new UI-focused fields.
    """
    # Given: A mock database session and a mock prediction object
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    # Set a post time 10 minutes into the future
    future_post_time = datetime.now(timezone.utc) + timedelta(minutes=10)

    mock_prediction = PredictionORM(
        prediction_id="pred_1",
        race_key="race_1",
        status="pending",
        race_local_datetime=future_post_time,
        score_total=85.5
    )
    mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_prediction]

    # When
    response = client.get("/predictions/active")

    # Then
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    prediction_response = data[0]

    assert prediction_response["prediction_id"] == "pred_1"
    assert prediction_response["score_total"] == 85.5
    # The calculated minutes_to_post should be slightly less than 10
    assert 9.9 < prediction_response["minutes_to_post"] < 10.0
