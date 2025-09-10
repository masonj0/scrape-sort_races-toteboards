import asyncio
import pandas as pd
from io import StringIO
from datetime import datetime, UTC
from typing import List, Optional

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..fetcher import get_page_content


class BetfairDataScientistAdapter(BaseAdapterV3):
    """
    Adapter for the Betfair Data Scientist API (Iggy-Joey model).
    """

    SOURCE_ID = "betfair_data_scientist"
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"

    async def fetch(self) -> List[NormalizedRace]:
        """
        Fetches and parses data from the Betfair Data Scientist API.
        """
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"
        csv_data = await get_page_content(url)
        return self.parse_races(csv_data)

    def parse_races(self, csv_content: str) -> List[NormalizedRace]:
        """
        Parses the CSV content from the API into a list of NormalizedRace objects.
        """
        if not csv_content:
            return []

        # Use pandas to read the CSV data
        data = StringIO(csv_content)
        df = pd.read_csv(data, dtype={"selection_id": str})

        # Rename columns for easier access
        df.rename(columns={"meetings.races.runners.ratedPrice": "rating"}, inplace=True)

        # Keep only the essential columns
        df = df[["market_id", "selection_id", "rating"]]

        races = {}
        for _, row in df.iterrows():
            race_id = str(row["market_id"])
            if race_id not in races:
                races[race_id] = NormalizedRace(
                    race_id=race_id,
                    track_name="Unknown", # Not in this API response
                    race_number=0, # Not in this API response
                    runners=[],
                )

            runner = NormalizedRunner(
                name=str(row["selection_id"]),
                program_number=0, # Not in this API response
                odds=row["rating"],
            )
            races[race_id].runners.append(runner)

        return list(races.values())
