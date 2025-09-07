import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from ..base import BaseAdapter, NormalizedRace, NormalizedRunner
from ..sync_fetcher import post_json_content


def parse_from_json(schedule_data: str, detail_data: str) -> List[NormalizedRace]:
    """
    Parses the two-stage JSON data from FanDuel's GraphQL API into a list of
    standardized race objects.
    """
    schedule = json.loads(schedule_data)
    detail = json.loads(detail_data)

    # Create a lookup dictionary for schedule information for efficient access
    schedule_lookup = {}
    for track in schedule.get("data", {}).get("scheduleRaces", []):
        for race_info in track.get("races", []):
            schedule_lookup[race_info["id"]] = race_info

    normalized_races = []
    for race_detail in detail.get("data", {}).get("races", []):
        race_id = race_detail.get("id")
        if not race_id or race_id not in schedule_lookup:
            continue

        race_schedule_info = schedule_lookup[race_id]

        runners = []
        for interest in race_detail.get("bettingInterests", []):
            runner_info = interest.get("runners", [{}])[0]
            if not runner_info.get("scratched"):
                odds_info = interest.get("currentOdds", {})
                odds_num = odds_info.get('numerator')
                odds_den = odds_info.get('denominator')

                if odds_num is not None and odds_den is not None:
                    try:
                        odds = float(odds_num / odds_den)
                    except ZeroDivisionError:
                        odds = None
                else:
                    odds = None

                runner = NormalizedRunner(
                    name=runner_info.get("horseName"),
                    program_number=interest.get("biNumber"),
                    scratched=runner_info.get("scratched", False),
                    odds=odds,
                )
                runners.append(runner)

        # If there are no non-scratched runners, we can skip this race.
        if not runners:
            continue

        normalized_race = NormalizedRace(
            race_id=race_id,
            track_name=race_schedule_info.get("track", {}).get("name"),
            race_number=int(race_schedule_info.get("number")),
            post_time=datetime.fromisoformat(race_schedule_info.get("postTime").replace("Z", "+00:00")),
            race_type=race_schedule_info.get("type", {}).get("code"),
            number_of_runners=len(runners),
            runners=runners,
        )
        normalized_races.append(normalized_race)

    return normalized_races


class FanDuelGraphQLAdapter(BaseAdapter):
    """
    Adapter for fetching and parsing data from the FanDuel GraphQL API.
    """
    SOURCE_ID = "fanduel"
    API_ENDPOINT = "https://api.racing.fanduel.com/cosmo/v1/graphql"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "content-type": "application/json"
    }
    SCHEDULE_QUERY = {
        "operationName": "getLhnInfo",
        "variables": {"withGreyhounds": False, "brand": "FDR", "product": "TVG5", "device": "Desktop", "noLoggedIn": True, "wagerProfile": "FDR-Generic"},
        "query": "query getLhnInfo($wagerProfile: String, $withGreyhounds: Boolean, $noLoggedIn: Boolean!, $product: String, $device: String, $brand: String) { scheduleRaces: tracks(profile: $wagerProfile) { id races( filter: {status: [\"MO\", \"O\", \"SK\", \"IC\"] allRaceClasses: $withGreyhounds} page: {results: 2, current: 0} sort: {byMTP: ASC} ) { id tvgRaceId mtp number postTime isGreyhound location { country __typename } track { id isFavorite @skip(if: $noLoggedIn) code name perfAbbr featured hasWagersToday @skip(if: $noLoggedIn) __typename } highlighted(product: $product, device: $device, brand: $brand) { description pinnedOrder action style __typename } promos(product: $product, brand: $brand) { rootParentPromoID isAboveTheLine promoPath isPromoTagShown __typename } type { code __typename } status { code __typename } video { onTvg onTvg2 __typename } __typename } __typename } }"
    }
    DETAIL_QUERY = {
        "operationName": "getGraphRaceBettingInterest",
        "variables": {"tvgRaceIds": [], "tvgRaceIdsBiPartial": [], "wagerProfile": "FDR-Generic"},
        "query": "query getGraphRaceBettingInterest($tvgRaceIds: [Long]) { races: races( tvgRaceIds: $tvgRaceIds ) { id tvgRaceId bettingInterests { biNumber runners { horseName scratched } currentOdds { numerator denominator } } } }"
    }


    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetches schedule and detail data from the FanDuel GraphQL endpoint.
        """
        try:
            # Fetch the race schedule
            schedule_response = post_json_content(self.API_ENDPOINT, json_payload=self.SCHEDULE_QUERY)
            schedule_json = schedule_response.json()

            # Extract tvgRaceIds from the schedule
            tvg_race_ids = []
            for track in schedule_json.get("data", {}).get("scheduleRaces", []):
                for race in track.get("races", []):
                    if race.get("tvgRaceId"):
                        tvg_race_ids.append(race["tvgRaceId"])

            if not tvg_race_ids:
                logging.warning("No races found in the schedule.")
                return {"schedule": schedule_response.text, "detail": "{}"}

            # Fetch the details for the found races
            detail_query = self.DETAIL_QUERY.copy()
            detail_query["variables"]["tvgRaceIds"] = tvg_race_ids

            detail_response = post_json_content(self.API_ENDPOINT, json_payload=detail_query)

            return {
                "schedule": schedule_response.text,
                "detail": detail_response.text
            }

        except Exception as e:
            logging.error(f"An error occurred while fetching data from FanDuel: {e}", exc_info=True)
            return {"schedule": "{}", "detail": "{}"}


    def parse_data(self, raw_data: Dict[str, Any]) -> List[NormalizedRace]:
        """
        Parses the raw FanDuel GraphQL data by calling the standalone function.
        """
        return parse_from_json(raw_data["schedule"], raw_data["detail"])
