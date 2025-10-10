# python_service/etl.py
# This module contains the ETL logic for the PostgreSQL data warehouse.
# Restored based on the 'Code Archaeology Report'.

import os
from typing import List
import pandas as pd
from sqlalchemy import create_engine

from .models import Race

class PostgresETL:
    """Data Warehouse ETL"""
    def __init__(self):
        db_url = os.getenv("POSTGES_URL", "postgresql://user:password@localhost/fortuna_dw")
        self.engine = create_engine(db_url)

    def process_and_load(self, analyzed_races: List[Race]):
        valid_for_historical = []
        quarantined = []
        for race in analyzed_races:
            errors = []
            if not race.venue: errors.append("Missing venue")
            if race.race_number is None: errors.append("Missing race_number")
            if not errors:
                valid_for_historical.append({
                    "race_id": race.id,
                    "track_name": race.venue,
                    "race_number": race.race_number,
                    "post_time": race.start_time,
                    "qualification_score": race.qualification_score
                })
            else:
                quarantined.append({
                    "race_id": race.id,
                    "quarantine_reason": ", ".join(errors),
                    "raw_data": race.json()
                })
        if valid_for_historical:
            pd.DataFrame(valid_for_historical).to_sql('historical_races', self.engine, if_exists='append', index=False)
        if quarantined:
            pd.DataFrame(quarantined).to_sql('quarantine_races', self.engine, if_exists='append', index=False)