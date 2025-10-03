# python_service/adapters/pointsbet_adapter.py
from .base import BaseAdapter
class PointsBetAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(source_name="PointsBet", base_url="https://api.pointsbet.com")
    async def fetch_races(self, date, http_client):
        return {'races': [], 'source_info': {'name': self.source_name}}