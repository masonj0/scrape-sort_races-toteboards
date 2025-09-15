"""
Core data models for the Paddock Parser application.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Runner:
    name: str
    odds: Optional[float]
    is_winner: bool = False

@dataclass
class Race:
    race_id: str
    venue: str
    race_time: str
    race_number: int
    is_handicap: bool
    number_of_runners: Optional[int] = None
    source: str = "" # The new field for the original source
    runners: List[Runner] = field(default_factory=list)
    sources: List[str] = field(default_factory=list) # New field for merged provenance

# V4 Models for the Polyglot Renaissance
from datetime import datetime

@dataclass
class NormalizedRunner:
    name: str

@dataclass
class NormalizedRace:
    track: str
    race_number: int
    race_time: datetime
    runners: List[NormalizedRunner] = field(default_factory=list)
