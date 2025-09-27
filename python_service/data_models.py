# data_models.py
# Pydantic models for database interaction

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class DatabaseRace(BaseModel):
    race_id: str
    track_name: str
    race_number: int
    post_time: datetime
    raw_data_json: str
    checkmate_score: float
    qualified: bool
    trifecta_factors_json: str
    updated_at: datetime

class AdapterStatus(BaseModel):
    adapter_name: str
    status: str
    last_run: datetime
    races_found: int
    error_message: Optional[str] = None