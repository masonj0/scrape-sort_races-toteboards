# src/checkmate_v7/services.py
import logging
from typing import List
from .base import BaseAdapterV7, DefensiveFetcher
from .models import Race
from .adapters import PRODUCTION_ADAPTERS, DEVELOPMENT_ADAPTERS
from .database import get_db_session

class DataSourceOrchestrator:
    def __init__(self, use_all_adapters=False):
        self.fetcher = DefensiveFetcher()
        if use_all_adapters:
            adapters_to_use = PRODUCTION_ADAPTERS + DEVELOPMENT_ADAPTERS
            logging.info(f"Initializing orchestrator with ALL {len(adapters_to_use)} adapters.")
        else:
            adapters_to_use = PRODUCTION_ADAPTERS
            logging.info(f"Initializing orchestrator with {len(adapters_to_use)} PRODUCTION adapters.")

        self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in adapters_to_use]

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        for adapter in self.adapters:
            adapter_id = adapter.__class__.__name__
            races = []
            error_message = None
            status = "OK"
            notes = ""
            try:
                races = adapter.fetch_races()
                if races:
                    notes = f"Successfully parsed {len(races)} races."
                else:
                    notes = "No upcoming races found on source."
                statuses.append({"adapter_id": adapter_id, "status": status, "races_found": len(races), "notes": notes, "error_message": None})
                if races:
                    all_races.extend(races)
            except Exception as e:
                logging.error(f"Adapter {adapter_id} failed: {e}", exc_info=True)
                status = "ERROR"
                error_message = str(e)
                notes = f"API Error: {error_message}"
                statuses.append({"adapter_id": adapter_id, "status": status, "error_message": error_message, "notes": notes, "races_found": 0})
        return all_races, statuses