import pytest
from src.checkmate_v7 import models

def test_prediction_model():
    """Tests the Prediction model creation."""
    pred = models.Prediction(
        prediction_id="test_id",
        race_key="test_race",
        model_version="7.0",
        score_total=8.1,
        qualified_flag=True
    )
    assert pred.prediction_id == "test_id"
    assert pred.qualified_flag is True
