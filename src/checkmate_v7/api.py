"""
Checkmate V7: `api.py` - THE CONDUCTOR
"""
from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime, timezone, timedelta

# These will be placeholder imports until other files are created
from .models import PredictionSchema, PredictionORM
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Placeholder for get_db_session
def get_db_session():
    # In a real setup, this would use a configured database URL
    # Using an in-memory sqlite for this recreation
    engine = create_engine("sqlite:///:memory:")
    # This is also a placeholder, as the PredictionORM table won't exist
    # until we have a proper setup. The test will mock this away.
    from .models import Base
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

app = FastAPI()

@app.get("/predictions/active", response_model=List[PredictionSchema])
def get_active_predictions():
    """
    Returns a list of all active (pending) predictions with calculated
    time-to-post and scores.
    """
    session = get_db_session()
    try:
        active_preds = session.query(PredictionORM).filter_by(status='pending').all()

        response_data = []
        for pred in active_preds:
            minutes_to_post = 0.0
            if pred.race_local_datetime:
                now_utc = datetime.now(timezone.utc)
                # Assume race_local_datetime is naive, make it timezone-aware (UTC)
                post_time_utc = pred.race_local_datetime.replace(tzinfo=timezone.utc)
                time_diff_seconds = (post_time_utc - now_utc).total_seconds()
                minutes_to_post = time_diff_seconds / 60

            pred_schema = PredictionSchema(
                prediction_id=pred.prediction_id,
                race_key=pred.race_key,
                status=pred.status,
                minutes_to_post=minutes_to_post,
                score_total=pred.score_total
            )
            response_data.append(pred_schema)

        return response_data
    except SQLAlchemyError as e:
        # A real logger would be used here
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        session.close()
