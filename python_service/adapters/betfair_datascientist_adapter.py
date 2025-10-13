# python_service/adapters/betfair_datascientist_adapter.py

import pandas as pd
import requests
from datetime import datetime
from io import StringIO

from ..models_v3 import NormalizedRace, NormalizedRunner
from .base_v3 import BaseAdapterV3
from ..utils.text import normalize_course_name

class BetfairDataScientistAdapter(BaseAdapterV3):
    ADAPTER_NAME = "BetfairDataScientist"

    def __init__(self, model_name: str, url: str, enabled: bool = True, priority: int = 100):
        super().__init__(f"{self.ADAPTER_NAME}_{model_name}", enabled, priority)
        self.model_name = model_name
        self.url = url
        self.logger.info(f"Initialized BetfairDataScientistAdapter for model: {self.model_name}")

    def fetch_and_normalize(self) -> list[NormalizedRace]:
        if not self.is_enabled():
            self.logger.debug(f"Adapter '{self.get_name()}' is disabled. Skipping.")
            return []

        try:
            full_url = self._build_url()
            self.logger.info(f"Fetching data from {full_url}")
            response = requests.get(full_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            return self._normalize_df(df)
        except Exception as e:
            self.logger.error(f"An unexpected error in {self.get_name()}: {e}", exc_info=True)
            return []

    def _normalize_df(self, df: pd.DataFrame) -> list[NormalizedRace]:
        df = df.rename(columns={
            "meetings.races.bfExchangeMarketId": "market_id",
            "meetings.races.runners.bfExchangeSelectionId": "selection_id",
            "meetings.races.runners.ratedPrice": "rated_price",
            "meetings.races.raceName": "race_name",
            "meetings.name": "meeting_name",
            "meetings.races.raceNumber": "race_number",
            "meetings.races.runners.runnerName": "runner_name",
            "meetings.races.runners.clothNumber": "saddle_cloth"
        })
        normalized_races = []
        for market_id, group in df.groupby("market_id"):
            race_info = group.iloc[0]
            runners = [
                NormalizedRunner(
                    runner_id=str(row.get('selection_id')),
                    name=str(row.get('runner_name')),
                    saddle_cloth=str(row.get('saddle_cloth', '')),
                    odds_decimal=float(row.get('rated_price', 0.0))
                ) for _, row in group.iterrows()
            ]
            race = NormalizedRace(
                race_key=str(market_id),
                track_key=normalize_course_name(str(race_info.get('meeting_name', ''))),
                start_time_iso=datetime.now().isoformat(),
                race_name=str(race_info.get('race_name', '')),
                runners=runners,
                source_ids=[self.get_name()],
            )
            normalized_races.append(race)
        self.logger.info(f"Normalized {len(normalized_races)} races from {self.model_name}.")
        return normalized_races

    def _build_url(self) -> str:
        todays_date = datetime.now().strftime("%Y-%m-%d")
        return f"{self.url}{todays_date}&presenter=RatingsPresenter&csv=true"
