# python_service/models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

class OddsData(BaseModel):
    win: Optional[Decimal] = None
    source: str
    last_updated: datetime

class Runner(BaseModel):
    number: int
    name: str
    scratched: bool = False
    odds: Dict[str, OddsData] = Field(default_factory=dict)
    jockey: Optional[str] = None
    trainer: Optional[str] = None
    morning_line_odds: Optional[str] = None

class Race(BaseModel):
    id: str
    venue: str
    race_number: int
    start_time: datetime
    runners: List[Runner]
    source: str
    race_name: Optional[str] = None
    race_url: Optional[str] = None
    distance: Optional[str] = None
    qualification_score: Optional[float] = None

class RaceDay(BaseModel):
    track_name: str
    races: List[Race]