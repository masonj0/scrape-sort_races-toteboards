from typing import List, Optional
from datetime import datetime
import logging
import json

from ..base import BaseAdapterV7
from ..models import Race, Runner


class FanDuelApiAdapterV7(BaseAdapterV7):
    """
    Adapter for the FanDuel GraphQL API.
    This has been refactored to use the legacy, more stable GraphQL endpoint
    which is not protected by aggressive bot detection.
    """
    SOURCE_ID = "fanduel_api"
    API_URL = "https://api.racing.fanduel.com/cosmo/v1/graphql"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    SCHEDULE_QUERY = {
        "operationName": "getLhnInfo",
        "variables": {"withGreyhounds": False, "brand": "FDR", "product": "TVG5", "device": "Desktop", "noLoggedIn": True, "wagerProfile": "FDR-Generic"},
        "query": "query getLhnInfo($wagerProfile: String, $withGreyhounds: Boolean, $noLoggedIn: Boolean!, $product: String, $device: String, $brand: String) { scheduleRaces: tracks(profile: $wagerProfile) { id races( filter: {status: [\"MO\", \"O\", \"SK\", \"IC\"], allRaceClasses: $withGreyhounds}, page: {results: 20, current: 0}, sort: {byMTP: ASC} ) { id tvgRaceId mtp number postTime isGreyhound location { country __typename } track { id isFavorite @skip(if: $noLoggedIn) code name perfAbbr featured hasWagersToday @skip(if: $noLoggedIn) __typename } highlighted(product: $product, device: $device, brand: $brand) { description pinnedOrder action style __typename } promos(product: $product, brand: $brand) { rootParentPromoID isAboveTheLine promoPath isPromoTagShown __typename } type { code __typename } status { code __typename } video { onTvg onTvg2 __typename } __typename } __typename } }"
    }
    DETAIL_QUERY = {
        "operationName": "getGraphRaceBettingInterest",
        "variables": {"tvgRaceIds": [], "tvgRaceIdsBiPartial": [], "wagerProfile": "FDR-Generic"},
        "query": "query getGraphRaceBettingInterest($tvgRaceIds: [Long], $tvgRaceIdsBiPartial: [Long], $wagerProfile: String) { races: races( tvgRaceIds: $tvgRaceIds profile: $wagerProfile sorts: [{byRaceNumber: ASC}] ) { id tvgRaceId bettingInterests { biNumber saddleColor numberColor favorite currentOdds { numerator denominator __typename } morningLineOdds { numerator denominator __typename } recentOdds(pages: [{current: 0, results: 4}]) { odd trending __typename } biPools { wagerType { id code name __typename } poolRunnersData { amount __typename } __typename } runners { runnerId entityRunnerId scratched horseName age sex weight med jockey trainer dob hasJockeyChanges ...timeformFragment handicapping { freePick { number info __typename } __typename } ...handicappingFragment __typename } __typename } ...Probables ...RacePools ...WillPays __typename } racesBiPartial: races( tvgRaceIds: $tvgRaceIdsBiPartial profile: $wagerProfile sorts: [{byRaceNumber: ASC}] ) { id tvgRaceId bettingInterests { biNumber saddleColor numberColor favorite currentOdds { numerator denominator __typename } morningLineOdds { numerator denominator __typename } runners { runnerId entityRunnerId scratched horseName jockey trainer hasJockeyChanges winProbability __typename } __typename } __typename } } fragment handicappingFragment on Runner { ownerName sire damSire dam handicapping { speedAndClass { avgClassRating highSpeed avgSpeed lastClassRating avgDistance __typename } averagePace { finish numRaces middle early __typename } jockeyTrainer { places jockeyName trainerName shows wins starts __typename } snapshot { powerRating daysOff horseWins horseStarts __typename } pastResults { totalNumberOfStarts numberOfFirstPlace numberOfSecondPlace numberOfThirdPlace winPercentage winPercentageRanking top3Percentage top3PercentageRanking __typename } __typename } __typename } fragment timeformFragment on Runner { timeform { analystsComments silkUrl silkUrlSvg freePick { number info __typename } flags { horseInFocus warningHorse jockeyUplift trainerUplift horsesForCoursePos horsesForCourseNeg hotTrainer coldTrainer highestLastSpeedRating sectionalFlag significantImprover jockeyInForm clearTopRated interestingJockeyBooking firstTimeBlinkers __typename } __typename } __typename } fragment Probables on Race { probables { amount minWagerAmount wagerType { id code name __typename } betCombos { runner1 runner2 payout __typename } __typename } __typename } fragment RacePools on Race { racePools { wagerType { id code name __typename } amount __typename } __typename } __typename } fragment WillPays on Race { willPays { wagerAmount payOffType type { id code name __typename } payouts { bettingInterestNumber payoutAmount __typename } legResults { legNumber winningBi __typename } __typename } __typename } "
    }


    def fetch_races(self) -> List[Race]:
        """
        Fetches schedule and detail data from the FanDuel GraphQL endpoint in two stages.
        """
        try:
            # Stage 1: Fetch the race schedule
            schedule_response = self.fetcher.post(self.API_URL, json_data=self.SCHEDULE_QUERY, headers=self.HEADERS)
            if not schedule_response or "data" not in schedule_response:
                logging.warning(f"{self.SOURCE_ID}: Did not receive valid schedule response.")
                return []

            # Extract tvgRaceIds from the schedule
            tvg_race_ids = []
            for track in schedule_response.get("data", {}).get("scheduleRaces", []):
                for race in track.get("races", []):
                    if race.get("tvgRaceId"):
                        tvg_race_ids.append(race["tvgRaceId"])

            if not tvg_race_ids:
                logging.info(f"{self.SOURCE_ID}: No upcoming races found in the schedule.")
                return []

            # Stage 2: Fetch the details for the found races
            detail_query = self.DETAIL_QUERY.copy()
            detail_query["variables"]["tvgRaceIds"] = tvg_race_ids

            detail_response = self.fetcher.post(self.API_URL, json_data=detail_query, headers=self.HEADERS)
            if not detail_response:
                logging.warning(f"{self.SOURCE_ID}: Did not receive detail response.")
                return []

            return self._parse_races(schedule_response, detail_response)

        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to fetch or parse races: {e}", exc_info=True)
            return []


    def _parse_races(self, schedule_data: dict, detail_data: dict) -> List[Race]:
        """
        Parses the two-stage JSON data from FanDuel's GraphQL API into a list of
        standardized V7 Race objects.
        """
        # Create a lookup dictionary for schedule information for efficient access
        schedule_lookup = {}
        for track in schedule_data.get("data", {}).get("scheduleRaces", []):
            for race_info in track.get("races", []):
                schedule_lookup[race_info["id"]] = race_info

        normalized_races = []
        for race_detail in detail_data.get("data", {}).get("races", []):
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

                    decimal_odds = None
                    if odds_num is not None and odds_den is not None and odds_den != 0:
                        decimal_odds = (odds_num / odds_den) + 1.0

                    runner = Runner(
                        name=runner_info.get("horseName"),
                        program_number=interest.get("biNumber"),
                        jockey=runner_info.get("jockey"),
                        trainer=runner_info.get("trainer"),
                        odds=decimal_odds,
                    )
                    runners.append(runner)

            if not runners:
                continue

            normalized_race = Race(
                race_id=race_id,
                track_name=race_schedule_info.get("track", {}).get("name"),
                race_number=int(race_schedule_info.get("number")),
                post_time=self._to_datetime(race_schedule_info.get("postTime")),
                race_type=race_schedule_info.get("type", {}).get("code"),
                number_of_runners=len(runners),
                runners=runners,
            )
            normalized_races.append(normalized_race)

        return normalized_races

    def _to_datetime(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
