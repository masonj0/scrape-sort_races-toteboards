from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """
    Abstract base class for all data source adapters.
    """

    @abstractmethod
    def fetch_data(self):
        """
        Fetch raw data from the source.
        """
        pass

    @abstractmethod
    def parse_data(self, raw_data):
        """
        Parse the raw data into a standardized format.
        """
        pass
