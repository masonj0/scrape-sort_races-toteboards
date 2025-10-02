# python_service/adapters/base.py

import logging
import abc

class BaseAdapter(abc.ABC):
    """
    An abstract base class for all data source adapters, enforcing a
    consistent interface.
    """

    def __init__(self, fetcher):
        """
        Initializes the adapter with a shared fetcher instance.

        :param fetcher: An instance of a fetcher class (e.g., DefensiveFetcher)
                        that handles the actual HTTP requests.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fetcher = fetcher

    @abc.abstractmethod
    def fetch_races(self) -> dict:
        """
        Abstract method to fetch race data from the source.

        This method must be implemented by all subclasses. It should return
        a dictionary with a 'success' key (boolean) and either a 'data' key
        (on success) or an 'error_details' key (on failure).
        """
        raise NotImplementedError("Each adapter must implement the fetch_races method.")