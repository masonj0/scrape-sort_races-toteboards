"""
Core data models for the Paddock Parser application.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class Runner:
    name: str
    odds: str

@dataclass
class Race:
    race_id: str
    venue: str
    race_time: str
    is_handicap: bool
    source: str = "" # The new field for the original source
    runners: List[Runner] = field(default_factory=list)
    sources: List[str] = field(default_factory=list) # New field for merged provenance
