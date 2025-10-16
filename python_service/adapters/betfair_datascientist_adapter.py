# python_service/adapters/betfair_datascientist_adapter.py

from datetime import datetime
from io import StringIO
from typing import Any
from typing import List

import pandas as pd
import requests
import structlog

from ..models import Race
from ..models import Runner
from ..utils.text import normalize_course_name
from .base_v3 import BaseAdapterV3


class BetfairDataScientistAdapter(BaseAdapterV3):
    ADAPTER_NAME = "BetfairDataScientist"

    def __init__(self, model_name: str, url: str, enabled: bool = True, priority: int = 100, config=None):
        source_name = f"{self.ADAPTER_NAME}_{model_name}"
        super().__init__(source_name=source_name, base_url=url)
        self.model_name = model_name
        self.url = url
        self._enabled = enabled
        self._priority = priority
        self.config = config

    async def _fetch_data(self, date: str) -> Any:
        if not self._enabled:
            self.logger.debug(f"Adapter '{self.source_name}' is disabled. Skipping.")
            return None

        try:
            full_url = self._build_url(date)
            self.logger.info(f"Fetching data from {full_url}")
            response = await asyncio.to_thread(requests.get, full_url)
            response.raise_for_status()
            return StringIO(response.text)
        except Exception as e:
            self.logger.error(f"An unexpected error in {self.source_name}: {e}", exc_info=True)
            return None

    def _parse_races(self, raw_data: Any) -> List[Race]:
        df = pd.read_csv(raw_data)
        df = df.rename(
            columns={
                "meetings.races.bfExchangeMarketId": "market_id",
                "meetings.races.runners.bfExchangeSelectionId": "selection_id",
                "meetings.races.runners.ratedPrice": "rated_price",
                "meetings.races.raceName": "race_name",
                "meetings.name": "meeting_name",
                "meetings.races.raceNumber": "race_number",
                "meetings.races.runners.runnerName": "runner_name",
                "meetings.races.runners.clothNumber": "saddle_cloth",
            }
        )
        races = []
        for market_id, group in df.groupby("market_id"):
            race_info = group.iloc[0]
            runners = [
                Runner(
                    name=str(row.get("runner_name")),
                    number=int(row.get("saddle_cloth", 0)),
                    odds=float(row.get("rated_price", 0.0)),
                )
                for _, row in group.iterrows()
            ]
            race = Race(
                id=str(market_id),
                venue=normalize_course_name(str(race_info.get("meeting_name", ""))),
                race_number=int(race_info.get("race_number", 0)),
                start_time=datetime.now(),
                runners=runners,
                source=self.source_name,
            )
            races.append(race)
        self.logger.info(f"Normalized {len(races)} races from {self.model_name}.")
        return races

    def _build_url(self, date: str) -> str:
        return f"{self.url}{date}&presenter=RatingsPresenter&csv=true"
