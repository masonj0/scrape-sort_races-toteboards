# python_service/adapters/pointsbet_adapter.py

import logging
from ..models import RaceData, RunnerData
from .base import BaseAdapter

class PointsBetAdapter(BaseAdapter):
    SOURCE_ID = "pointsbet"
    def fetch_races(self):
        self.logger.warning(f"Adapter {self.SOURCE_ID} is a stub and returns no data.")
        return {'success': True, 'data': []}