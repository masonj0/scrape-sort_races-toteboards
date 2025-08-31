import json
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any

from ..base import BaseAdapter, NormalizedRace, NormalizedRunner


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
                odds = float(odds_num) if odds_num is not None else None

                runner = NormalizedRunner(
                    name=runner_info.get("horseName"),
                    program_number=interest.get("biNumber"),
                    scratched=runner_info.get("scratched", False),
                    jockey=runner_info.get("jockey"),
                    trainer=runner_info.get("trainer"),
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
            minutes_to_post=race_schedule_info.get("mtp"),
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
        "query": "query getGraphRaceBettingInterest($tvgRaceIds: [Long], $tvgRaceIdsBiPartial: [Long], $wagerProfile: String) { races: races( tvgRaceIds: $tvgRaceIds profile: $wagerProfile sorts: [{byRaceNumber: ASC}] ) { id tvgRaceId bettingInterests { biNumber saddleColor numberColor favorite currentOdds { numerator denominator __typename } morningLineOdds { numerator denominator __typename } recentOdds(pages: [{current: 0, results: 4}]) { odd trending __typename } biPools { wagerType { id code name __typename } poolRunnersData { amount __typename } __typename } runners { runnerId entityRunnerId scratched horseName age sex weight med jockey trainer dob hasJockeyChanges ...timeformFragment handicapping { freePick { number info __typename } __typename } ...handicappingFragment __typename } __typename } ...Probables ...RacePools ...WillPays __typename } racesBiPartial: races( tvgRaceIds: $tvgRaceIdsBiPartial profile: $wagerProfile sorts: [{byRaceNumber: ASC}] ) { id tvgRaceId bettingInterests { biNumber saddleColor numberColor favorite currentOdds { numerator denominator __typename } morningLineOdds { numerator denominator __typename } runners { runnerId entityRunnerId scratched horseName jockey trainer hasJockeyChanges winProbability __typename } __typename } __typename } }\\n\\nfragment handicappingFragment on Runner { ownerName sire damSire dam handicapping { speedAndClass { avgClassRating highSpeed avgSpeed lastClassRating avgDistance __typename } averagePace { finish numRaces middle early __typename } jockeyTrainer { places jockeyName trainerName shows wins starts __typename } snapshot { powerRating daysOff horseWins horseStarts __typename } pastResults { totalNumberOfStarts numberOfFirstPlace numberOfSecondPlace numberOfThirdPlace winPercentage winPercentageRanking top3Percentage top3PercentageRanking __typename } __typename } __typename }\\n\\nfragment timeformFragment on Runner { timeform { analystsComments silkUrl silkUrlSvg freePick { number info __typename } flags { horseInFocus warningHorse jockeyUplift trainerUplift horsesForCoursePos horsesForCourseNeg hotTrainer coldTrainer highestLastSpeedRating sectionalFlag significantImprover jockeyInForm clearTopRated interestingJockeyBooking firstTimeBlinkers __typename } __typename } __typename }\\n\\nfragment Probables on Race { probables { amount minWagerAmount wagerType { id code name __typename } betCombos { runner1 runner2 payout __typename } __typename } __typename }\\n\\nfragment RacePools on Race { racePools { wagerType { id code name __typename } amount __typename } __typename } __typename }\\n\\nfragment WillPays on Race { willPays { wagerAmount payOffType type { id code name __typename } payouts { bettingInterestNumber payoutAmount __typename } legResults { legNumber winningBi __typename } __typename } __typename } }"
    }


    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetches schedule and detail data from the FanDuel GraphQL endpoint.
        """
        with httpx.Client() as client:
            try:
                # Fetch the race schedule
                schedule_response = client.post(self.API_ENDPOINT, json=self.SCHEDULE_QUERY, headers=self.HEADERS)
                schedule_response.raise_for_status()
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

                detail_response = client.post(self.API_ENDPOINT, json=detail_query, headers=self.HEADERS)
                detail_response.raise_for_status()

                return {
                    "schedule": schedule_response.text,
                    "detail": detail_response.text
                }

            except httpx.RequestError as e:
                logging.error(f"An error occurred while requesting {e.request.url!r}: {e}")
                return {"schedule": "{}", "detail": "{}"}
            except httpx.HTTPStatusError as e:
                logging.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
                return {"schedule": "{}", "detail": "{}"}


    def parse_data(self, raw_data: Dict[str, Any]) -> List[NormalizedRace]:
        """
        Parses the raw FanDuel GraphQL data by calling the standalone function.
        """
        return parse_from_json(raw_data["schedule"], raw_data["detail"])
