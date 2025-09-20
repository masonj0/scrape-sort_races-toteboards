"""
The new, modern Betfair Data Scientist API adapter.
"""
from typing import List
from datetime import datetime, timezone
import logging
from io import StringIO
import pandas as pd

from ..base import BaseAdapterV7, DefensiveFetcher
from ..models import Race, Runner


class BetfairModernAdapter(BaseAdapterV7):
    """
    Adapter for the Betfair Data Scientist API (CSV format).
    This is the modern implementation, refactored into its own module.
    """
    SOURCE_ID = "betfair_data_scientist"
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"

    async def fetch_races(self) -> List[Race]:
        """Fetches and parses data from the Betfair Data Scientist API."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"

        csv_data = await self.fetcher.fetch(url, response_type='text')
        if not csv_data:
            return []
        return self._parse_races(csv_data)

    def _parse_races(self, csv_content: str) -> List[Race]:
        """Parses the CSV content from the API into a list of Race objects."""
        if not csv_content:
            return []

        try:
            data = StringIO(csv_content)
            # Ensure selection_id is read as a string to preserve it
            df = pd.read_csv(data, dtype={"selection_id": str})
            # The 'rating' is effectively the odds in this context
            df.rename(columns={"meetings.races.runners.ratedPrice": "rating"}, inplace=True)
            df = df[["market_id", "selection_id", "rating"]]

            races = {}
            for _, row in df.iterrows():
                race_id = str(row["market_id"])
                if race_id not in races:
                    races[race_id] = Race(
                        race_id=race_id,
                        track_name="Unknown", # Not available in this API response
                        race_number=None, # Not available in this API response
                        runners=[],
                    )

                runner = Runner(
                    name=str(row["selection_id"]), # Use selection_id as the unique name
                    program_number=None, # Not available in this API response
                    odds=row["rating"], # Use the 'rating' as the odds
                )
                races[race_id].runners.append(runner)

            return list(races.values())
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to parse CSV data: {e}")
            return []
