# python_service/models_v3.py
# Defines the data structures for the V3 adapter architecture.

from dataclasses import dataclass
from dataclasses import field
from typing import List


@dataclass
class NormalizedRunner:
    runner_id: str
    name: str
    saddle_cloth: str
    odds_decimal: float


@dataclass
class NormalizedRace:
    race_key: str
    track_key: str
    start_time_iso: str
    race_name: str
    runners: List[NormalizedRunner] = field(default_factory=list)
    source_ids: List[str] = field(default_factory=list)
