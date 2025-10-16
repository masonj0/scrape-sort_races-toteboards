# python_service/models.py

from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


# --- Configuration for Aliases (BUG #4 Fix) ---
class FortunaBaseModel(BaseModel):
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# --- Core Data Models ---
class OddsData(FortunaBaseModel):
    win: Optional[Decimal] = None
    place: Optional[Decimal] = None
    show: Optional[Decimal] = None
    source: str
    last_updated: datetime


class Runner(FortunaBaseModel):
    id: Optional[str] = None
    name: str
    number: Optional[int] = Field(None, alias="saddleClothNumber")
    scratched: bool = False
    odds: Dict[str, OddsData] = {}
    jockey: Optional[str] = None
    trainer: Optional[str] = None


class Race(FortunaBaseModel):
    id: str
    venue: str
    race_number: int = Field(..., alias="raceNumber")
    start_time: datetime = Field(..., alias="startTime")
    runners: List[Runner]
    source: str
    qualification_score: Optional[float] = Field(None, alias="qualificationScore")
    favorite: Optional[Runner] = None
    race_name: Optional[str] = None
    distance: Optional[str] = None


class SourceInfo(FortunaBaseModel):
    name: str
    status: str
    races_fetched: int = Field(..., alias="racesFetched")
    fetch_duration: float = Field(..., alias="fetchDuration")
    error_message: Optional[str] = Field(None, alias="errorMessage")


class AggregatedResponse(FortunaBaseModel):
    races: List[Race]
    source_info: List[SourceInfo] = Field(..., alias="sourceInfo")


class QualifiedRacesResponse(FortunaBaseModel):
    criteria: Dict[str, Any]
    races: List[Race]


class TipsheetRace(FortunaBaseModel):
    race_id: str = Field(..., alias="raceId")
    track_name: str = Field(..., alias="trackName")
    race_number: int = Field(..., alias="raceNumber")
    post_time: str = Field(..., alias="postTime")
    score: float
    factors: Any  # JSON string stored as Any
