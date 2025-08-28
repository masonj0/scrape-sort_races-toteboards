from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NormalizedRunner:
    """
    A normalized representation of a single runner in a race.
    """
    name: str
    odds: Optional[str] = None
    runner_number: Optional[int] = None
    cloth_number: Optional[int] = None


@dataclass
class NormalizedRace:
    """
    A normalized representation of a single race.
    This structure is what all adapters should output.
    """
    race_id: str
    track_name: str
    race_number: int
    number_of_runners: int
    runners: List[NormalizedRunner] = field(default_factory=list)
    race_url: Optional[str] = None
    timestamp: Optional[int] = None


class BaseAdapter(ABC):
    """
    Abstract base class for all data adapters.
    """
    SOURCE_ID = "base"

    @abstractmethod
    def fetch(self):
        """
        Fetches the raw data from the source.
        """
        pass

    @abstractmethod
    def parse(self, data):
        """
        Parses the raw data into a list of NormalizedRace objects.
        """
        pass

    def get_races(self):
        """
        Orchestrates the fetching and parsing of data.
        """
        raw_data = self.fetch()
        return self.parse(raw_data)


class BaseAdapterV3(ABC):
    """
    Abstract base class for V3 adapters that work with HTML content.
    """
    SOURCE_ID = "base_v3"
    url = ""

    @abstractmethod
    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """
        Parses HTML content to extract race data.
        """
        pass
