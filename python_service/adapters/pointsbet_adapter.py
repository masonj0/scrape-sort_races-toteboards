# python_service/adapters/pointsbet_adapter.py

from .base import BaseAdapter

class PointsBetAdapter(BaseAdapter):
    async def fetch_races(self):
        return {'success': True, 'data': []}