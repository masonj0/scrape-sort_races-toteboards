# python_service/adapters/harness_adapter.py
from datetime import datetime
from typing import AsyncGenerator

from ..models import OddsData
from ..models import Race
from ..models import Runner
from ..utils.odds import parse_odds_to_decimal
from .base import BaseAdapter


class HarnessAdapter(BaseAdapter):
    """Adapter for fetching US harness racing data from data.ustrotting.com."""

    SOURCE_NAME = "USTrotting"
    BASE_URL = "https://data.ustrotting.com/api/racenet/racing/"

    def __init__(self, config=None):
        super().__init__(self.SOURCE_NAME, self.BASE_URL)

    async def fetch_races(self, date: str) -> AsyncGenerator[Race, None]:
        """Fetches all harness races for a given date."""
        card_data = await self.make_request(method="get", url=f"{self.BASE_URL}card/{date}")
        if not card_data or not card_data.get("meetings"):
            return

        for meeting in card_data["meetings"]:
            track_name = meeting.get("track", {}).get("name")
            for race_data in meeting.get("races", []):
                yield self._parse_race(race_data, track_name, date)

    def _parse_race(self, race_data: dict, track_name: str, date: str) -> Race:
        """Parses a single race from the USTA API into a Race object."""
        race_number = race_data.get("raceNumber", 0)
        post_time_str = race_data.get("postTime", "00:00 AM")
        start_time = self._parse_post_time(date, post_time_str)

        runners = []
        for runner_data in race_data.get("runners", []):
            odds_str = runner_data.get("morningLineOdds", "")
            # Ensure odds are fractional for parsing
            if "/" not in odds_str and odds_str.isdigit():
                odds_str = f"{odds_str}/1"

            odds = {}
            win_odds = parse_odds_to_decimal(odds_str)
            if win_odds and win_odds < 999:
                odds = {self.SOURCE_NAME: OddsData(win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now())}

            runners.append(
                Runner(
                    number=runner_data.get("postPosition", 0),
                    name=runner_data.get("horse", {}).get("name", "Unknown Horse"),
                    odds=odds,
                    scratched=runner_data.get("scratched", False),
                )
            )

        return Race(
            id=f"ust_{track_name.lower().replace(' ', '')}_{date}_{race_number}",
            venue=track_name,
            race_number=race_number,
            start_time=start_time,
            runners=runners,
            source=self.SOURCE_NAME,
        )

    def _parse_post_time(self, date: str, post_time: str) -> datetime:
        """Parses a time string like '07:00 PM' into a timezone-aware datetime object."""
        from zoneinfo import ZoneInfo

        dt_str = f"{date} {post_time}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        # Assume Eastern Time for USTA data, a common standard for US racing.
        eastern = ZoneInfo("America/New_York")
        return naive_dt.replace(tzinfo=eastern)
