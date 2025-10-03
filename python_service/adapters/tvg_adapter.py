# python_service/adapters/tvg_adapter.py
from .base import BaseAdapter
class TVGAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(source_name="TVG", base_url="https://api.tvg.com")
    async def fetch_races(self, date, http_client):
        return {'races': [], 'source_info': {'name': self.source_name}}