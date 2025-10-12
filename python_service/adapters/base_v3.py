# python_service/adapters/base_v3.py
# Defines the base class for the V3 adapter architecture.

from abc import ABC, abstractmethod
import structlog

from ..models_v3 import NormalizedRace

class BaseAdapterV3(ABC):
    def __init__(self, name: str, enabled: bool = True, priority: int = 100):
        self._name = name
        self._enabled = enabled
        self._priority = priority
        self.logger = structlog.get_logger(adapter_name=self.get_name())

    def get_name(self) -> str:
        return self._name

    def is_enabled(self) -> bool:
        return self._enabled

    @abstractmethod
    def fetch_and_normalize(self) -> list[NormalizedRace]:
        raise NotImplementedError
