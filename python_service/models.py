# python_service/models.py

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class RunnerData(BaseModel):
    name: str
    odds: Optional[float] = None

class RaceData(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None # Some sources may not provide this
    post_time: datetime
    runners: List[RunnerData]
    source: str

class FormattedRace(BaseModel):
    race_id: str
    track: str
    race: Optional[int]
    time: str
    runners: List[Dict[str, str]]

class APIResponse(BaseModel):
    success: bool
    data: Optional[List[FormattedRace]] = None
    error: Optional[str] = None