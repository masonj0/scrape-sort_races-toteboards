"""
Checkmate V7: `models.py` - THE BLUEPRINT
"""
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import (Column, Integer, String, Float, DateTime, Boolean, JSON,
 ForeignKey)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel

Base = declarative_base()

# --- ORM Models ---

class PredictionORM(Base):
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
    race_local_datetime = Column(DateTime, nullable=True)

    join = relationship("JoinORM", back_populates="prediction", uselist=False)

class ResultORM(Base):
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

    join = relationship("JoinORM", back_populates="result", uselist=False)

class JoinORM(Base):
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

    prediction = relationship("PredictionORM", back_populates="join")
    result = relationship("ResultORM", back_populates="join")

class SettingsORM(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(JSON)

class AdapterStatusORM(Base):
    __tablename__ = 'adapters_status'
    adapter_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    last_ok_at = Column(DateTime)
    rate_limit_until = Column(DateTime)

# --- Pydantic Schemas ---

class PredictionSchema(BaseModel):
    prediction_id: str
    race_key: str
    status: str
    qualified_flag: Optional[bool] = None
    stake_used: Optional[float] = None
    score_total: Optional[float] = None
    minutes_to_post: Optional[float] = None

    class Config:
        orm_mode = True

class PerformanceMetricsSchema(BaseModel):
    total_bets: int
    win_rate: float
    roi_percent: float
    net_profit: float
    confidence_interval: List[float]
    p_value: float
    sample_size: int

class ActionStatusSchema(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    celery: str

# --- Adapter Data Models ---

class Runner(BaseModel):
    name: str
    odds: Optional[float] = None
    program_number: Optional[int] = None
    jockey: Optional[str] = None
    trainer: Optional[str] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    race_type: Optional[str] = None
    number_of_runners: Optional[int] = None
    runners: List[Runner]
