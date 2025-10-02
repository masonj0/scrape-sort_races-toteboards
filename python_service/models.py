# python_service/models.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Runner(BaseModel):
    name: str
    odds: Optional[float] = None

class Race(BaseModel):
    id: str
    venue: str
    race_number: int
    race_time: datetime
    runners: List[Runner]
    source: str