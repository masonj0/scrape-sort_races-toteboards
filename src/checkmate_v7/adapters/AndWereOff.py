# src/checkmate_v7/adapters/AndWereOff.py

import logging
import re
from datetime import date, datetime, timezone
from typing import List, Optional, Dict
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from ..base import BaseAdapterV7
from ..models import Race, Runner

def _convert_odds_to_float(odds_str: Optional[str]) -> Optional[float]:
    if not odds_str or not isinstance(odds_str, str): return None
    odds_str = odds_str.strip().upper()
    if odds_str in ['SP', 'SCRATCHED']: return None
    if odds_str in ['EVS', 'EVENS']: return 2.0
    if '/' in odds_str:
        try:
            num, den = map(int, odds_str.split('/'))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, ZeroDivisionError): return None
    try: return float(odds_str)
    except (ValueError, TypeError): return None

class SkySportsAdapter(BaseAdapterV7):
    SOURCE_ID = "skysports"
    BASE_URL = "https://www.skysports.com"

    def fetch_races(self) -> List[Race]:
        index_url = f"{self.BASE_URL}/racing/racecards"
        index_html = self.fetcher.get(index_url, response_type='text')
        if not index_html: return []
        soup = BeautifulSoup(index_html, "lxml")
        race_urls = [f"{self.BASE_URL}{link['href']}" for link in soup.select("a.sdc-site-racing-meetings__event-link[href]")]
        all_races = []
        for url in race_urls[:5]: # Limit for speed
            detail_html = self.fetcher.get(url, response_type='text')
            if detail_html:
                race = self._parse_race_details(detail_html, url)
                if race: all_races.append(race)
        return all_races

    def _parse_race_details(self, html: str, url: str) -> Optional[Race]:
        soup = BeautifulSoup(html, "lxml")
        track_name = soup.select_one("h1.sdc-site-racing-header__title").text.strip()
        post_time_str = soup.select_one("span.sdc-site-racing-header__time").text.strip()
        post_time = datetime.combine(date.today(), datetime.strptime(post_time_str, "%H:%M").time())
        runners = [Runner(name=item.select_one("h4 a").text.strip(), program_number=int(item.select_one("div strong").text.strip()), odds=_convert_odds_to_float(item.select_one(".sdc-site-racing-card__betting-odds").text.strip())) for item in soup.select("div.sdc-site-racing-card__item") if item.select_one("h4 a")]
        if not runners: return None
        return Race(race_id=f"{self.SOURCE_ID}_{url.split('/')[-1]}", track_name=track_name, post_time=post_time, runners=[r for r in runners if r.odds])

class AtTheRacesAdapter(BaseAdapterV7):
    SOURCE_ID = "attheraces"
    BASE_URL = "https://www.attheraces.com"

    def fetch_races(self) -> List[Race]:
        index_html = self.fetcher.get(f"{self.BASE_URL}/racecards", response_type='text')
        if not index_html: return []
        soup = BeautifulSoup(index_html, 'html.parser')
        links = [{"url": self.BASE_URL + a['href'], "track": a.find_previous("h2").text.strip().replace(" Racecards",""), "time": a.select_one("span.h7").text.strip()[:5]} for a in soup.select("a.a--plain[href*='/racecard/']")]
        all_races = []
        for link in links[:5]:
            html = self.fetcher.get(link["url"], response_type='text')
            if html:
                race = self._parse_single_race(html, link)
                if race: all_races.append(race)
        return all_races

    def _parse_single_race(self, html: str, details: Dict) -> Optional[Race]:
        soup = BeautifulSoup(html, 'html.parser')
        runners = [Runner(name=card.select_one(".horse-name a").text.strip(), program_number=int(card.select_one(".runner-number").text.strip()), odds=_convert_odds_to_float(card.select_one(".odds").text.strip())) for card in soup.select("div.runner-card") if card.select_one(".horse-name a")]
        if not runners: return None
        return Race(race_id=f'{self.SOURCE_ID}_{details["url"].split("/")[-2]}_{details["url"].split("/")[-1]}', track_name=details['track'], runners=[r for r in runners if r.odds])

class BetfairDataScientistAdapter(BaseAdapterV7):
    """
    Production adapter for Betfair Data Scientist API.
    Fetches CSV data and converts to standardized Race objects.
    """
    SOURCE_ID = "betfair_data_scientist"
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"

    def fetch_races(self) -> List[Race]:
        """Fetches and parses data from the Betfair Data Scientist API."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"
        logging.info(f"Fetching Betfair CSV data from: {url}")

        csv_data = self.fetcher.get(url, response_type='text')
        if not csv_data:
            logging.warning(f"{self.SOURCE_ID}: No CSV data returned.")
            return []

        return self._parse_races(csv_data)

    def _parse_races(self, csv_content: str) -> List[Race]:
        """Parses the CSV content from the API into a list of Race objects."""
        try:
            data = StringIO(csv_content)
            df = pd.read_csv(data, dtype={"selection_id": str})
            df.rename(columns={"meetings.races.runners.ratedPrice": "rating"}, inplace=True)
            df = df[["market_id", "selection_id", "rating"]]

            races = {}
            for _, row in df.iterrows():
                race_id = str(row["market_id"])
                if race_id not in races:
                    races[race_id] = Race(
                        race_id=race_id,
                        track_name="Betfair Exchange",
                        race_number=None, # Not available in this data source
                        runners=[],
                        source=self.SOURCE_ID
                    )

                runner = Runner(
                    name=str(row["selection_id"]),
                    program_number=None, # Not available in this data source
                    odds=row["rating"],
                )
                races[race_id].runners.append(runner)

            return list(races.values())
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to parse CSV data: {e}", exc_info=True)
            return []

class FanDuelApiAdapter(BaseAdapterV7):
    SOURCE_ID = "fanduel_api"
    API_URL = "https://api.racing.fanduel.com/cosmo/v1/graphql"
    QUERY = {"operationName": "GetRacingSchedule", "variables": {"input": {"product": "FAN_DUEL_RACING", "jurisdiction": "USA"}}, "query": "query GetRacingSchedule($input: RacingScheduleInput!) { racingSchedule(input: $input) { schedule { date tracks { id name races { id raceNumber postTime runners { id runnerNumber runnerName scratched } } } } } }"}

    def fetch_races(self) -> List[Race]:
        data = self.fetcher.post(self.API_URL, json_data=self.QUERY, response_type='json')
        if not data: return []
        all_races = []
        try:
            for track in data.get("data", {}).get("scheduleRaces", []):
                if not track: continue
                track_name = track.get("id", "").split("-")[-1].replace("_", " ")
                for race_info in track.get("races", []):
                    runners = [Runner(name=r.get("runnerName"), program_number=r.get("programNumber")) for r in race_info.get("runners", []) if not r.get("scratched")]
                    all_races.append(Race(race_id=race_info.get("id"), track_name=track_name, race_number=int(race_info.get("raceNumber")), runners=runners))
        except Exception as e: logging.error(f"{self.SOURCE_ID}: Failed during parsing: {e}")
        return all_races

class TVGAdapter(BaseAdapterV7):
    """Adapter for the TVG.com mobile API."""
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"

    def fetch_races(self) -> List[Race]:
        """Fetches today's races from the TVG mobile API."""
        logging.info(f"Fetching races from {self.SOURCE_ID}")
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')

        if not response_data or 'races' not in response_data:
            logging.warning(f"{self.SOURCE_ID}: No 'races' key found in API response.")
            return []

        return self._parse_races(response_data['races'])

    def _parse_races(self, races_data: List[Dict]) -> List[Race]:
        """Parses the JSON race data into standardized Race objects."""
        all_races = []
        for race_info in races_data:
            try:
                runners = []
                for runner_info in race_info.get('runners', []):
                    if runner_info.get('scratched'):
                        continue

                    odds_val = self._parse_odds(runner_info.get('odds'))
                    if odds_val is None:
                        continue # Skip runners without valid odds

                    runners.append(Runner(
                        name=runner_info.get('horseName', 'Unknown Horse'),
                        program_number=runner_info.get('programNumber'),
                        odds=odds_val
                    ))

                if not runners:
                    continue

                post_time = self._parse_time(race_info.get('postTime'))

                race = Race(
                    race_id=f"tvg_{race_info.get('raceId')}",
                    track_name=race_info.get('trackName', 'Unknown Track'),
                    race_number=race_info.get('raceNumber'),
                    post_time=post_time,
                    runners=runners,
                    number_of_runners=len(runners),
                    source=self.SOURCE_ID
                )
                all_races.append(race)
            except Exception as e:
                logging.warning(f"Skipping malformed TVG race due to error: {e}")
                continue
        return all_races

    def _parse_odds(self, odds_data: Optional[Dict]) -> Optional[float]:
        """Parses the odds structure from the TVG API."""
        if not odds_data or odds_data.get('morningLine') is None:
            return None
        try:
            # TVG odds can be fractional "N/D" or decimal
            odds_str = odds_data['morningLine']
            if '/' in odds_str:
                num, den = map(int, odds_str.split('/'))
                return (num / den) + 1.0
            return float(odds_str)
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parses ISO 8601 timestamp."""
        if not time_str: return None
        try:
            # Example: "2025-09-26T20:30:00Z"
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            return None