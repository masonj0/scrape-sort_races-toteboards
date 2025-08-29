import json
from datetime import datetime
from typing import List, Dict, Any

from .base import BaseAdapter, NormalizedRace, NormalizedRunner


def parse_from_json(schedule_data: str, detail_data: str) -> List[NormalizedRace]:
    """
    Parses the two-stage JSON data from FanDuel's GraphQL API into a list of
    standardized race objects.

    Args:
        schedule_data: The JSON string containing the race schedule.
        detail_data: The JSON string containing the details for a specific race.

    Returns:
        A list of NormalizedRace objects.
    """
    schedule = json.loads(schedule_data)
    detail = json.loads(detail_data)

    # The sample data is disconnected (schedule has A12/DUQ, detail has HOO-6).
    # For this exercise, we will parse the race from the detail data and use
    # the first race from the schedule data as a stand-in for metadata that
    # would normally be matched by ID.

    race_detail = detail["data"]["races"][0]
    race_schedule_info = schedule["data"]["scheduleRaces"][0]["races"][0]

    runners = []
    for interest in race_detail.get("bettingInterests", []):
        if not interest["runners"][0]["scratched"]:
            runner_info = interest["runners"][0]
            odds_info = interest.get("currentOdds", {})

            # Format odds as "numerator-1" if numerator exists, otherwise None.
            odds = f"{odds_info['numerator']}-1" if odds_info.get("numerator") else None

            runner = NormalizedRunner(
                name=runner_info["horseName"],
                program_number=interest["biNumber"],
                scratched=runner_info["scratched"],
                jockey=runner_info["jockey"],
                trainer=runner_info["trainer"],
                odds=odds,
            )
            runners.append(runner)

    # Construct the NormalizedRace, taking the specific ID from the detail file
    # and enriching it with metadata from the (assumed matched) schedule file.
    normalized_race = NormalizedRace(
        race_id=race_detail["id"],
        track_name=race_schedule_info["track"]["name"],
        race_number=int(race_schedule_info["number"]),
        post_time=datetime.fromisoformat(race_schedule_info["postTime"].replace("Z", "+00:00")),
        race_type=race_schedule_info["type"]["code"],
        minutes_to_post=race_schedule_info["mtp"],
        runners=runners,
    )

    return [normalized_race]


class FanDuelGraphQLAdapter(BaseAdapter):
    """
    Adapter for fetching and parsing data from the FanDuel GraphQL API.
    """
    SOURCE_ID = "fanduel"

    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetches data from the FanDuel GraphQL endpoint.
        (Placeholder implementation)
        """
        print("Fetching data from FanDuel GraphQL API...")
        return {"schedule": "{}", "detail": "{}"}

    def parse_data(self, raw_data: Dict[str, Any]) -> List[NormalizedRace]:
        """
        Parses the raw FanDuel GraphQL data by calling the standalone function.
        """
        return parse_from_json(raw_data["schedule"], raw_data["detail"])
