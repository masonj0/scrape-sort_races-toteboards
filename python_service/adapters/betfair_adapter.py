# python_service/adapters/betfair_adapter.py

from .base import BaseAdapter

class BetfairAdapter(BaseAdapter):
    async def fetch_races(self):
        return {'success': True, 'data': []}