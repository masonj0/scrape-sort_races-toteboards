"""
Checkmate V7: `models.py` - THE BLUEPRINT
"""
from datetime import datetime
from typing import List, Optional
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
    race_local_datetime = Column(DateTime, nullable=True) # The post time of the race
    model_version = Column(String, nullable=False)
    status = Column(String, default='pending', index=True)
    score_total = Column(Float)
    # Other fields would be here in a full implementation...

    # Placeholder for relationship, will need ResultORM and JoinORM
    # join = relationship("JoinORM", back_populates="prediction", uselist=False)

# --- Pydantic Schemas ---

class PredictionSchema(BaseModel):
    prediction_id: str
    race_key: str
    status: str
    minutes_to_post: float
    score_total: Optional[float] = None

    class Config:
        from_attributes = True
