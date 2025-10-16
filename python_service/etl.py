# python_service/etl.py
# ETL pipeline for populating the historical data warehouse

import json
import logging
import os
from datetime import date

import requests
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScribesArchivesETL:
    def __init__(self):
        self.postgres_url = os.getenv("POSTGRES_URL")
        self.api_key = os.getenv("API_KEY")
        self.api_base_url = "http://localhost:8000"
        self.engine = self._get_db_engine()

    def _get_db_engine(self):
        if not self.postgres_url:
            logger.warning("POSTGRES_URL not set. ETL will be skipped.")
            return None
        try:
            return create_engine(self.postgres_url)
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}", exc_info=True)
            return None

    def _fetch_race_data(self, target_date: date) -> list:
        """Fetches aggregated race data from the local API."""
        if not self.api_key:
            raise ValueError("API_KEY not found in environment.")

        url = f"{self.api_base_url}/api/races?race_date={target_date.isoformat()}"
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json().get("races", [])

    def _validate_and_transform(self, race: dict) -> tuple:
        """Validates a race dictionary and transforms it for insertion."""
        if not all(k in race for k in ["id", "venue", "race_number", "start_time", "runners"]):
            return None, "Missing core fields (id, venue, race_number, start_time, runners)"

        active_runners = [r for r in race.get("runners", []) if not r.get("scratched")]

        transformed = {
            "race_id": race["id"],
            "venue": race["venue"],
            "race_number": race["race_number"],
            "start_time": race["start_time"],
            "source": race.get("source"),
            "qualification_score": race.get("qualification_score"),
            "field_size": len(active_runners),
        }
        return transformed, None

    def run(self, target_date: date):
        if not self.engine:
            return

        logger.info(f"Starting ETL process for {target_date.isoformat()}...")
        try:
            races = self._fetch_race_data(target_date)
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Failed to fetch race data: {e}", exc_info=True)
            return

        clean_records = []
        quarantined_records = []

        for race in races:
            transformed, reason = self._validate_and_transform(race)
            if transformed:
                clean_records.append(transformed)
            else:
                quarantined_records.append(
                    {
                        "race_id": race.get("id"),
                        "source": race.get("source"),
                        "payload": json.dumps(race),
                        "reason": reason,
                    }
                )

        with self.engine.connect() as connection:
            try:
                with connection.begin():  # Transaction block
                    if clean_records:
                        # Using ON CONFLICT to prevent duplicates
                        stmt = text(
                            """
                            INSERT INTO historical_races (
                                race_id, venue, race_number, start_time, source,
                                qualification_score, field_size
                            )
                            VALUES (
                                :race_id, :venue, :race_number, :start_time, :source,
                                :qualification_score, :field_size
                            )
                            ON CONFLICT (race_id) DO NOTHING;
                        """
                        )
                        connection.execute(stmt, clean_records)
                        logger.info(f"Inserted/updated {len(clean_records)} records into historical_races.")

                    if quarantined_records:
                        stmt = text("""
                            INSERT INTO quarantined_races (race_id, source, payload, reason)
                            VALUES (:race_id, :source, :payload::jsonb, :reason);
                        """)
                        connection.execute(stmt, quarantined_records)
                        logger.warning(f"Moved {len(quarantined_records)} records to quarantine.")
            except SQLAlchemyError as e:
                logger.error(f"Database transaction failed: {e}", exc_info=True)

        logger.info("ETL process finished.")


def run_etl_for_yesterday():
    from datetime import timedelta

    yesterday = date.today() - timedelta(days=1)
    etl = ScribesArchivesETL()
    etl.run(yesterday)
