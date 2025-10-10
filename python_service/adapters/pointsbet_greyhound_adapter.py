# python_service/adapters/pointsbet_greyhound_adapter.py

import structlog
from datetime import datetime
from typing import Dict, Any, List
import httpx

from .base import BaseAdapter
from ..models import Race

log = structlog.get_logger(__name__)

class PointsBetGreyhoundAdapter(BaseAdapter):
    """TODO: This is a placeholder adapter. It will not be active until the correct sportId is found."""
    def __init__(self, config):
        super().__init__(
            source_name="PointsBet Greyhound",
            base_url="https://api.au.pointsbet.com"
        )
        self.api_key = config.POINTSBET_API_KEY

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        # TODO: This adapter is a placeholder and is not registered in the engine.
        # To enable, find the correct sportId for Greyhound Racing and register the adapter.
        log.warning("PointsBetGreyhoundAdapter: This adapter is a non-functional placeholder.")
        return self._format_response([], start_time, is_success=True, error_message="Adapter is a placeholder.")

    def _format_response(self, races: List[Race], start_time: datetime, is_success: bool = True, error_message: str = None) -> Dict[str, Any]:
        fetch_duration = (datetime.now() - start_time).total_seconds()
        return {
            'races': races,
            'source_info': {
                'name': self.source_name,
                'status': 'SUCCESS' if is_success else 'FAILED',
                'races_fetched': len(races),
                'error_message': error_message,
                'fetch_duration': fetch_duration
            }
        }