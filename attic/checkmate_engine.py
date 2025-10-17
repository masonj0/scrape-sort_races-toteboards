# checkmate_engine.py
# This is a self-contained, portable script combining the best of Checkmate V7.

import logging
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Union, Optional, Dict
from datetime import date, datetime, timezone
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
import argparse
from tabulate import tabulate
from colorama import Fore, Style, init as colorama_init

# --- Part 1: Settings ---
class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///./checkmate_v7.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    LOG_LEVEL: str = Field(default="INFO")
    ODDS_API_KEY: Optional[str] = Field(default=None, description="The API key for The Odds API.")
    QUALIFICATION_SCORE: float = Field(default=75.0, description="Minimum score to qualify.")
    FIELD_SIZE_OPTIMAL_MIN: int = Field(default=4)
    FIELD_SIZE_OPTIMAL_MAX: int = Field(default=6)
    FIELD_SIZE_ACCEPTABLE_MIN: int = Field(default=7)
    FIELD_SIZE_ACCEPTABLE_MAX: int = Field(default=8)
    FIELD_SIZE_OPTIMAL_POINTS: int = Field(default=30)
    FIELD_SIZE_ACCEPTABLE_POINTS: int = Field(default=10)
    FIELD_SIZE_PENALTY_POINTS: int = Field(default=-20)
    FAV_ODDS_POINTS: int = Field(default=30)
    MAX_FAV_ODDS: float = Field(default=3.5)
    SECOND_FAV_ODDS_POINTS: int = Field(default=40)
    MIN_2ND_FAV_ODDS: float = Field(default=4.0)

    class Config:
        env_file = ".env"
        case_sensitive = False
settings = Settings()

# --- Part 2: Models ---
class Runner(BaseModel):
    name: str
    odds: Optional[float] = None
    program_number: Optional[int] = None
    jockey: Optional[str] = None
    trainer: Optional[str] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    race_type: Optional[str] = None
    number_of_runners: Optional[int] = None
    runners: List[Runner]
    source: Optional[str] = None

class HorseSchema(BaseModel):
    id: Optional[str] = None
    name: str
    number: Optional[int] = None
    jockey: Optional[str] = None
    trainer: Optional[str] = None
    odds: Optional[float] = None
    morningLine: Optional[float] = None
    speed: Optional[int] = None
    class_rating: Optional[int] = None
    form: Optional[str] = None
    lastRaced: Optional[str] = None

class RaceDataSchema(BaseModel):
    id: Optional[str] = None
    track: Optional[str] = None
    raceNumber: Optional[int] = None
    postTime: Optional[str] = None
    horses: List[HorseSchema]
    conditions: Optional[str] = None
    distance: Optional[str] = None
    surface: Optional[str] = None
    checkmateScore: Optional[float] = None
    qualified: Optional[bool] = None
    trifectaFactors: Optional[Dict] = None

# --- Part 3: Base Fetcher & Adapter ---
class DefensiveFetcher:
    """The battle-tested, subprocess curl-based fetcher."""
    def get(self, url: str, headers: dict = None, response_type: str = 'auto') -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1"]
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout
            if response_type == 'text': return response_text
            if response_type == 'json': return json.loads(response_text)
            try: return json.loads(response_text)
            except json.JSONDecodeError: return response_text
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

    def post(self, url: str, json_data: dict, headers: dict = None, response_type: str = 'json') -> Union[dict, str, None]:
        try:
            command = ["curl", "-s", "-L", "-X", "POST", "--tlsv1.2", "--http1.1"]
            final_headers = headers.copy() if headers else {}
            final_headers['Content-Type'] = 'application/json'
            for key, value in final_headers.items():
                command.extend(["-H", f"{key}: {value}"])
            command.extend(["-d", json.dumps(json_data)])
            command.append(url)
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
            response_text = result.stdout
            return json.loads(response_text) if response_type == 'json' else response_text
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logging.error(f"CRITICAL: curl POST failed for {url}. Details: {e}")
            return None

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher
    @abstractmethod
    def fetch_races(self) -> List[Race]:
        raise NotImplementedError

# --- Part 4: Production Adapters ---
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
        for url in race_urls[:5]:
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
        return Race(race_id=f"{self.SOURCE_ID}_{url.split('/')[-1]}", track_name=track_name, post_time=post_time, runners=[r for r in runners if r.odds], source=self.SOURCE_ID)

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
        return Race(race_id=f'{self.SOURCE_ID}_{details["url"].split("/")[-2]}_{details["url"].split("/")[-1]}', track_name=details['track'], runners=[r for r in runners if r.odds], source=self.SOURCE_ID)

class TVGAdapter(BaseAdapterV7):
    SOURCE_ID = "tvg"
    BASE_URL = "https://mobile-api.tvg.com/api/mobile/races/today"
    def fetch_races(self) -> List[Race]:
        logging.info(f"Fetching races from {self.SOURCE_ID}")
        response_data = self.fetcher.get(self.BASE_URL, response_type='json')
        if not response_data or 'races' not in response_data:
            logging.warning(f"{self.SOURCE_ID}: No 'races' key found in API response.")
            return []
        return self._parse_races(response_data['races'])
    def _parse_races(self, races_data: List[Dict]) -> List[Race]:
        all_races = []
        for race_info in races_data:
            try:
                runners = []
                for runner_info in race_info.get('runners', []):
                    if runner_info.get('scratched'): continue
                    odds_val = self._parse_odds(runner_info.get('odds'))
                    if odds_val is None: continue
                    runners.append(Runner(name=runner_info.get('horseName', 'Unknown Horse'), program_number=runner_info.get('programNumber'), odds=odds_val))
                if not runners: continue
                post_time = self._parse_time(race_info.get('postTime'))
                race = Race(race_id=f"tvg_{race_info.get('raceId')}", track_name=race_info.get('trackName', 'Unknown Track'), race_number=race_info.get('raceNumber'), post_time=post_time, runners=runners, number_of_runners=len(runners), source=self.SOURCE_ID)
                all_races.append(race)
            except Exception as e:
                logging.warning(f"Skipping malformed TVG race due to error: {e}")
                continue
        return all_races
    def _parse_odds(self, odds_data: Optional[Dict]) -> Optional[float]:
        if not odds_data or odds_data.get('morningLine') is None: return None
        try:
            odds_str = odds_data['morningLine']
            if '/' in odds_str:
                num, den = map(int, odds_str.split('/'))
                return (num / den) + 1.0
            return float(odds_str)
        except (ValueError, TypeError, ZeroDivisionError): return None
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        if not time_str: return None
        try: return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError: return None

# --- Part 5: The Brain ---
class TrifectaAnalyzer:
    """The corrected analyzer, fully aligned with the settings module."""
    def analyze_race(self, race: RaceDataSchema) -> dict:
        score = 0
        reasons = []
        trifecta_factors = {}
        if not race.horses:
            return {"qualified": False, "checkmateScore": 0, "reasons": ["No horses data."], "trifectaFactors": {}}
        horses_with_odds = sorted([h for h in race.horses if h.odds], key=lambda h: h.odds)
        num_runners = len(horses_with_odds)
        if settings.FIELD_SIZE_OPTIMAL_MIN <= num_runners <= settings.FIELD_SIZE_OPTIMAL_MAX:
            points, ok, reason = settings.FIELD_SIZE_OPTIMAL_POINTS, True, f"Optimal field size ({num_runners} runners)"
        elif settings.FIELD_SIZE_ACCEPTABLE_MIN <= num_runners <= settings.FIELD_SIZE_ACCEPTABLE_MAX:
            points, ok, reason = settings.FIELD_SIZE_ACCEPTABLE_POINTS, True, f"Acceptable field size ({num_runners} runners)"
        else:
            points, ok, reason = settings.FIELD_SIZE_PENALTY_POINTS, False, f"Field size not ideal ({num_runners} runners)"
        score += points
        reasons.append(reason)
        trifecta_factors["fieldSize"] = {"points": points, "ok": ok, "reason": reason}
        if num_runners >= 2:
            favorite, second_favorite = horses_with_odds[0], horses_with_odds[1]
            if favorite.odds <= settings.MAX_FAV_ODDS:
                points, ok, reason = settings.FAV_ODDS_POINTS, True, f"Favorite odds OK ({favorite.odds})"
            else:
                points, ok, reason = 0, False, f"Favorite odds too high ({favorite.odds})"
            score += points
            reasons.append(reason)
            trifecta_factors["favoriteOdds"] = {"points": points, "ok": ok, "reason": reason}
            if second_favorite.odds >= settings.MIN_2ND_FAV_ODDS:
                points, ok, reason = settings.SECOND_FAV_ODDS_POINTS, True, f"2nd Favorite odds OK ({second_favorite.odds})"
            else:
                points, ok, reason = 0, False, f"2nd Favorite odds too low ({second_favorite.odds})"
            score += points
            reasons.append(reason)
            trifecta_factors["secondFavoriteOdds"] = {"points": points, "ok": ok, "reason": reason}
        else:
            reasons.append("Not enough runners with odds for full analysis.")
        return {"qualified": score >= settings.QUALIFICATION_SCORE, "checkmateScore": score, "reasons": reasons, "trifectaFactors": trifecta_factors}

# --- Part 6: The Conductor ---
PRODUCTION_ADAPTERS = [SkySportsAdapter, AtTheRacesAdapter, TVGAdapter]

class DataSourceOrchestrator:
    def __init__(self):
        self.fetcher = DefensiveFetcher()
        adapters_to_use = PRODUCTION_ADAPTERS
        logging.info(f"Initializing orchestrator with {len(adapters_to_use)} PRODUCTION adapters.")
        self.adapters: List[BaseAdapterV7] = [Adapter(self.fetcher) for Adapter in adapters_to_use]

    def get_races(self) -> tuple[list[Race], list[dict]]:
        all_races, statuses = [], []
        for adapter in self.adapters:
            adapter_id = adapter.__class__.__name__
            races, error_message, status, notes = [], None, "OK", ""
            try:
                races = adapter.fetch_races()
                if races: notes = f"Successfully parsed {len(races)} races."
                else: notes = "No upcoming races found on source."
                statuses.append({"adapter_id": adapter_id, "status": status, "races_found": len(races), "notes": notes, "error_message": None})
                if races: all_races.extend(races)
            except Exception as e:
                logging.error(f"Adapter {adapter_id} failed: {e}", exc_info=True)
                status, error_message = "ERROR", str(e)
                notes = f"API Error: {error_message}"
                statuses.append({"adapter_id": adapter_id, "status": status, "error_message": error_message, "notes": notes, "races_found": 0})
        return all_races, statuses

# --- Part 7: The Face (CLI) ---
def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

def convert_race_to_schema(race: Race) -> RaceDataSchema:
    horses = [HorseSchema(name=r.name, number=r.program_number, jockey=r.jockey, trainer=r.trainer, odds=r.odds) for r in race.runners if r.odds is not None]
    return RaceDataSchema(id=race.race_id, track=race.track_name, raceNumber=race.race_number, postTime=race.post_time.isoformat() if race.post_time else None, horses=horses)

def display_results(tipsheet, statuses):
    colorama_init()
    print("\\n--- " + Fore.CYAN + "Adapter Status" + Style.RESET_ALL + " ---")
    status_headers = {"adapter_id": "Adapter", "status": "Status", "races_found": "Races Found", "notes": "Notes"}
    status_data = []
    for s in statuses:
        status_color = Fore.GREEN if s['status'] == 'OK' else Fore.RED
        status_data.append([s['adapter_id'], status_color + s['status'] + Style.RESET_ALL, s['races_found'], s['notes']])
    print(tabulate(status_data, headers=status_headers, tablefmt="grid"))

    if not tipsheet:
        print("\\n" + Fore.YELLOW + "No qualified races found for the tipsheet." + Style.RESET_ALL)
        return

    print("\\n--- " + Fore.CYAN + "Checkmate Qualified Races" + Style.RESET_ALL + " ---")
    for race in tipsheet:
        print(f"\\n" + Fore.GREEN + f"Track: {race['trackName']} - Race: {race['raceNumber']} - Post Time: {race['postTime']} - Score: {race['checkmateScore']}" + Style.RESET_ALL)
        runner_headers = {"name": "Horse", "odds": "Odds", "program_number": "Program"}
        runner_data = [[r['name'], r['odds'], r.get('number')] for r in race['runners']]
        print(tabulate(runner_data, headers=runner_headers, tablefmt="psql"))

def main():
    parser = argparse.ArgumentParser(description="Checkmate V7 - The Ultimate Engine")
    parser.add_argument("--output", choices=["json", "table"], default="table", help="Specify the output format.")
    args = parser.parse_args()
    setup_logging()
    logging.info("--- Starting Checkmate V7: The Ultimate Engine ---")
    orchestrator = DataSourceOrchestrator()
    analyzer = TrifectaAnalyzer()
    logging.info("Fetching live race data...")
    races, statuses = orchestrator.get_races()
    logging.info(f"Orchestrator status: {statuses}")
    tipsheet = []
    if not races:
        logging.warning("No races were found by the orchestrator.")
    else:
        logging.info(f"Found {len(races)} races. Analyzing for Checkmate opportunities...")
        for race in races:
            race_schema = convert_race_to_schema(race)
            analysis = analyzer.analyze_race(race_schema)
            if analysis["qualified"]:
                logging.info(f"Checkmate QUALIFIED: {race.track_name} - Race {race.race_number} (Score: {analysis['checkmateScore']})")
                tipsheet.append({"trackName": race.track_name, "raceNumber": race.race_number, "postTime": race.post_time.isoformat() if race.post_time else None, "checkmateScore": analysis["checkmateScore"], "analysis": analysis, "runners": [r.model_dump() for r in race_schema.horses]})
            else:
                logging.info(f"Checkmate SKIPPED: {race.track_name} - Race {race.race_number} (Score: {analysis['checkmateScore']})")

    if args.output == "json":
        timestamp = datetime.now().strftime("%m%d_%Hh%M")
        output_filename = f"tipsheet_{timestamp}.json"
        logging.info(f"Writing {len(tipsheet)} qualified races to {output_filename}...")
        with open(output_filename, "w") as f:
            json.dump(tipsheet, f, indent=2)
        logging.info("Successfully generated tipsheet.")
    else:
        display_results(tipsheet, statuses)

    logging.info("--- Checkmate V7 Showcase Run Finished ---")

if __name__ == "__main__":
    main()