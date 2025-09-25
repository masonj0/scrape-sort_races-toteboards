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
    SOURCE_ID = "betfair_data_scientist"
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"

    def fetch_races(self) -> List[Race]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"
        csv_data = self.fetcher.get(url, response_type='text')
        if not csv_data: return []
        try:
            df = pd.read_csv(StringIO(csv_data))
            races = {}
            for _, row in df.iterrows():
                race_id = str(row["market_id"])
                if race_id not in races: races[race_id] = Race(race_id=race_id, track_name="Betfair Exchange", runners=[])
                races[race_id].runners.append(Runner(name=str(row["selection_id"]), odds=row["meetings.races.runners.ratedPrice"]))
            return list(races.values())
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to parse CSV: {e}")
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