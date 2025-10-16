#!/usr/bin/env python3
# This file was generated from the canonical adapter template.
from datetime import datetime
from typing import Any
from typing import Dict

import httpx
import structlog

from .base import BaseAdapter

log = structlog.get_logger(__name__)


class NYRABetsAdapter(BaseAdapter):
    """Adapter for nyrabets.com."""

    def __init__(self, config):
        super().__init__(source_name="NYRABets", base_url="https://nyrabets.com")

    async def fetch_races(self, date: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        start_time = datetime.now()
        log.warning("NYRABetsAdapter.fetch_races is a stub.")
        return self._format_response([], start_time, is_success=True, error_message="Not Implemented")
