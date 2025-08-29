from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


# --- Normalized Data Models ---

@dataclass
class NormalizedRunner:
    """
    A standardized representation of a single runner in a race.
    """
    name: str
    program_number: int
    scratched: bool = False
    jockey: Optional[str] = None
    trainer: Optional[str] = None
    odds: Optional[str] = None


@dataclass
class NormalizedRace:
    """
    A standardized representation of a single race.
    """
    race_id: str
    track_name: str
    race_number: int
    post_time: Optional[datetime] = None
    race_type: Optional[str] = None
    minutes_to_post: Optional[int] = None
    number_of_runners: Optional[int] = None
    runners: List[NormalizedRunner] = field(default_factory=list)


# --- Base Adapters ---

class BaseAdapter(ABC):
    """
    Abstract base class for data source adapters (V1 & V2 style).
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def fetch_data(self):
        pass

    @abstractmethod
    def parse_data(self, raw_data):
        pass


class BaseAdapterV3(ABC):
    """
    V3 of the Base Adapter for parsing complex, multi-race pages.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches and parses data to return a list of normalized races.
        """
        pass

    @abstractmethod
    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """
        Parses the full HTML content of a race day page.
        """
        pass
