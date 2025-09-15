"""
Checkmate V7: `models.py` - THE BLUEPRINT
"""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey)
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Prediction(Base):
    __tablename__ = 'predictions'
    prediction_id = Column(String, primary_key=True)
    race_key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String, nullable=False)
    status = Column(String, default='pending', index=True)
    favorite_candidate_selection_id = Column(String)
    favorite_candidate_name = Column(String)
    odds_snapshots = Column(JSON)
    score_components = Column(JSON)
    qualitative_analysis = Column(JSON)
    score_total = Column(Float)
    qualified_flag = Column(Boolean)
    confidence = Column(Float)
    stake_used = Column(Float)

class Result(Base):
    __tablename__ = 'results'
    result_id = Column(String, primary_key=True)
    race_key = Column(String, nullable=False, index=True)
    exact_time_off = Column(DateTime)
    result_source_adapter = Column(String)
    audit_version = Column(Integer)
    post_time_favorite_selection_id = Column(String)
    post_time_favorite_name = Column(String)
    finish_position = Column(Integer)
    place_paid_flag = Column(Boolean)
    place_payout_native = Column(Float)
    payout_unit = Column(Float)
    audit_status = Column(String, default='pending', index=True)
    validation_issues = Column(JSON)

class Join(Base):
    __tablename__ = 'joins'
    join_id = Column(String, primary_key=True)
    prediction_id = Column(String, ForeignKey('predictions.prediction_id'))
    result_id = Column(String, ForeignKey('results.result_id'))
    pnl_native = Column(Float)
    pnl_usd = Column(Float)
    stake_used = Column(Float)
    roi = Column(Float)
    audit_status = Column(String, default='pending', index=True)
    audit_notes = Column(JSON)

class PredictionSchema(BaseModel):
    prediction_id: str
    race_key: str
    status: str
    class Config: orm_mode = True
