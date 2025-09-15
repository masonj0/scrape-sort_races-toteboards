"""
Checkmate V7: `models.py` - THE BLUEPRINT
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import (Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field

# --- SQLAlchemy ORM Setup ---
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
    join = relationship("Join", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

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
    join = relationship("Join", back_populates="result", uselist=False, cascade="all, delete-orphan")

class Join(Base):
    __tablename__ = 'joins'
    join_id = Column(String, primary_key=True)
    prediction_id = Column(String, ForeignKey('predictions.prediction_id'), unique=True)
    result_id = Column(String, ForeignKey('results.result_id'), unique=True)
    pnl_native = Column(Float)
    pnl_usd = Column(Float)
    stake_used = Column(Float)
    roi = Column(Float)
    audit_status = Column(String, default='pending', index=True)
    audit_notes = Column(JSON)
    prediction = relationship("Prediction", back_populates="join")
    result = relationship("Result", back_populates="join")

class SettingsORM(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)

class AdapterStatusORM(Base):
    __tablename__ = 'adapters_status'
    adapter_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    last_ok_at = Column(DateTime)
    rate_limit_until = Column(DateTime)

# --- Pydantic Schemas (API Data Contracts) ---

class PredictionSchema(BaseModel):
    prediction_id: str
    race_key: str
    created_at: datetime
    status: str
    score_total: float
    favorite_candidate_name: str
    class Config: orm_mode = True

class PerformanceMetricsSchema(BaseModel):
    total_bets: int
    total_wins: int
    win_rate_percent: float
    total_pnl_usd: float
    total_staked_usd: float
    roi_percent: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    p_value: float

class ActionStatusSchema(BaseModel):
    status: str
    message: str
    details: Optional[Dict] = None

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    celery_status: str
    active_adapters: List[str]
