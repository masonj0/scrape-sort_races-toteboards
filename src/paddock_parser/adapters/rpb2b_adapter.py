import asyncio
import json
from datetime import datetime, UTC
from typing import Dict, List, Optional

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from ..fetcher import get_page_content


def _convert_odds_to_float(odds_str: Optional[str]) -> Optional[float]:
    """Converts fractional odds string to a float."""
    if not odds_str or not isinstance(odds_str, str):
        return None

    odds_str = odds_str.strip().upper()
    if "SP" in odds_str:
        return None

    if "/" in odds_str:
        try:
            numerator, denominator = map(int, odds_str.split("/"))
            if denominator == 0:
                return None
            return (numerator / denominator) + 1.0
        except (ValueError, ZeroDivisionError):
            return None
    return None


class Rpb2bAdapter(BaseAdapterV3):
    """
    Adapter for the Racing Post B2B API.
    """

    SOURCE_ID = "rpb2b"
    BASE_URL = "https://backend-us-racecards.widget.rpb2b.com/v2"

    async def fetch(self, race_ids: Optional[List[str]] = None) -> List[NormalizedRace]:
        """
        If `race_ids` are provided, fetches details for only those races.
        Otherwise, fetches all daily races.
        """
        if not race_ids:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            index_url = f"{self.BASE_URL}/racecards/daily/{today}"
            index_json_str = await get_page_content(index_url)

            if not index_json_str:
                return []

            race_list = json.loads(index_json_str)

            race_id_to_track_map = {
                race["id"]: course.get("name", "Unknown")
                for course in race_list
                for race in course.get("races", [])
            }
            race_ids = list(race_id_to_track_map.keys())
        else:
            # If race_ids are provided, we don't have the track map.
            # This is a limitation of this more efficient approach.
            # The track name will be parsed from the detail response if available,
            # otherwise it will be "Unknown".
            race_id_to_track_map = {}

        tasks = [
            get_page_content(f"{self.BASE_URL}/racecards/{race_id}?include=odds")
            for race_id in race_ids
        ]
        race_json_pages = await asyncio.gather(*tasks, return_exceptions=True)

        all_races = []
        for html_or_exc, race_id in zip(race_json_pages, race_ids):
            if isinstance(html_or_exc, Exception):
                continue

            race_detail = json.loads(html_or_exc)
            track_name = race_id_to_track_map.get(race_id, "Unknown")

            race = self._parse_race(race_detail, race_id, track_name)
            if race:
                all_races.append(race)

        return all_races

    def _parse_race(
        self, race_detail: Dict, race_id: str, track_name: str
    ) -> Optional[NormalizedRace]:
        """Parses the race detail JSON to extract all available data."""
        try:
            runners = []
            if race_detail.get("results") and race_detail["results"].get("result"):
                for runner_data in race_detail["results"]["result"]:
                    runner = NormalizedRunner(
                        name=runner_data.get("horseId"),
                        odds=_convert_odds_to_float(runner_data.get("startingPrice")),
                        program_number=runner_data.get("draw"),
                    )
                    runners.append(runner)

            return NormalizedRace(
                race_id=race_id,
                track_name=track_name,
                race_number=race_detail.get("raceNumber"),
                race_type=race_detail.get("raceType"),
                number_of_runners=race_detail.get("numberOfRunners"),
                runners=runners,
            )
        except (KeyError, TypeError):
            return None

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """This adapter is for live fetching, so offline parsing is not supported."""
        return []
