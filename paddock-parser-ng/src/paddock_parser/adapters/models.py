from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class NormalizedRunner:
    """
    A standardized representation of a single runner in a race.
    """
    name: str
    program_number: int
    scratched: bool
    jockey: str
    trainer: str
    odds: Optional[str]


@dataclass
class NormalizedRace:
    """
    A standardized representation of a single race, containing a list of its runners.
    """
    race_id: str
    track_name: str
    race_number: int
    post_time: datetime
    race_type: str
    minutes_to_post: int
    runners: List[NormalizedRunner]
