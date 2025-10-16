#!/usr/bin/env python3
# This file was generated from the canonical adapter template.
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

import httpx
import structlog

from ..models import Race
from .base import BaseAdapter

log = structlog.get_logger(__name__)


class TwinSpiresAdapter(BaseAdapter):
    """Adapter for twinspires.com."""

    def __init__(self, config):
        super().__init__(source_name="TwinSpires", base_url="https://www.twinspires.com")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        log.warning("TwinSpiresAdapter.fetch_races is a stub.")
        return self._format_response([], start_time)

    def _format_response(self, races: List[Race], start_time: datetime, **kwargs) -> Dict[str, Any]:
        return {
            "races": [],
            "source_info": {
                "name": self.source_name,
                "status": "SUCCESS",
                "races_fetched": 0,
                "error_message": "Not Implemented",
                "fetch_duration": (datetime.now() - start_time).total_seconds(),
            },
        }
