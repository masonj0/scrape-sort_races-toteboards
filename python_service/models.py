# python_service/models.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal

class OddsData(BaseModel):
    win: Optional[Decimal] = None
    source: str
    last_updated: datetime

    @field_validator('win')
    def win_must_be_positive(cls, v):
        if v is not None and v <= Decimal("1.0"):
            raise ValueError('Odds must be greater than 1.0')
        return v

class Runner(BaseModel):
    number: int = Field(..., gt=0, lt=100)
    name: str = Field(..., max_length=100)
    scratched: bool = False
    selection_id: Optional[int] = None # For Betfair Exchange integration
    odds: Dict[str, OddsData] = Field(default_factory=dict)
    jockey: Optional[str] = None
    trainer: Optional[str] = None

class Race(BaseModel):
    id: str
    venue: str
    race_number: int = Field(..., gt=0, lt=21)
    start_time: datetime
    runners: List[Runner]
    source: str
    qualification_score: Optional[float] = None
    race_name: Optional[str] = None
    distance: Optional[str] = None

    @field_validator('runners')
    def runner_numbers_must_be_unique(cls, v):
        numbers = [r.number for r in v]
        if len(numbers) != len(set(numbers)):
            raise ValueError('Runner numbers must be unique within a race')
        return v

class SourceInfo(BaseModel):
    name: str
    status: str
    races_fetched: int
    error_message: Optional[str] = None
    fetch_duration: float

class FetchMetadata(BaseModel):
    fetch_time: datetime
    sources_queried: List[str]
    sources_successful: int
    total_races: int

class AggregatedResponse(BaseModel):
    date: date
    races: List[Race]
    sources: List[SourceInfo]
    metadata: FetchMetadata