# python_service/adapters/tvg_adapter.py

from .base import BaseAdapter

class TVGAdapter(BaseAdapter):
    async def fetch_races(self):
        return {'success': True, 'data': []}