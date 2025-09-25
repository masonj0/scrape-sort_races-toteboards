# src/checkmate_v7/services.py
import logging
from typing import List
from .base import BaseAdapterV7, DefensiveFetcher
from .models import Race
from .adapters import PRODUCTION_ADAPTERS, DEVELOPMENT_ADAPTERS

class DataSourceOrchestrator:
    def __init__(self, use_all_adapters=False):
        self.fetcher = DefensiveFetcher()
        if use_all_adapters:
            self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in (PRODUCTION_ADAPTERS + DEVELOPMENT_ADAPTERS)]
        else:
            self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in PRODUCTION_ADAPTERS]

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        for adapter in self.adapters:
            adapter_id = adapter.SOURCE_ID
            races = []
            error_message = None
            status = "OK"
            notes = ""

            try:
                races = adapter.fetch_races()
                if races:
                    notes = f"Successfully parsed {len(races)} races."
                    logging.info(notes)
                    all_races.extend(races) # Keep collecting races
                else:
                    notes = "No upcoming races found on source."
                    logging.info(notes)
            except Exception as e:
                logging.error(f"Failed to fetch from {adapter_id}: {e}", exc_info=True)
                status = "ERROR"
                error_message = str(e)
                notes = f"API Error: {error_message}"

            statuses.append({
                "adapter_id": adapter_id,
                "status": status,
                "races_found": len(races),
                "error_message": error_message,
                "notes": notes,
                "last_run": "2025-09-25T03:27:50.777296+00:00"
            })
        return all_races, statuses

def get_db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from . import config
    from .models import Base
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()