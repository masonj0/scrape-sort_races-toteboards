"""
Checkmate V7: `services.py` - THE GATEWAY
"""
import logging
import asyncio
import random
import time
import anyio
import json
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from typing import List, Optional

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from celery import Celery
from io import StringIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from . import config, logic
from .models import AdapterStatusORM, PredictionORM, ResultORM, JoinORM, Base, Race, Runner

# --- Celery App Configuration ---
celery_app = Celery('tasks', broker=config.REDIS_URL)

# --- Celery Logging Integration ---
from celery.signals import after_setup_logger, after_setup_task_logger

@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logging(logger, **kwargs):
    """
    This function is connected to Celery's logging signals and
    reconfigures the logger to use our structured JSON format.
    """
    # Use the same handlers from the root logger
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)

    logger.propagate = False

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    async def __aenter__(self):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.last_failure_time = time.time()
        elif self.state == "half-open":
            self.failure_count = 0
            self.state = "closed"

class DefensiveFetcher:
    def __init__(self):
        self.circuit_breakers = {}

    async def fetch(self, url, headers=None, response_type='text'):
        return await self._request('GET', url, headers=headers, response_type=response_type)

    async def post(self, url, headers=None, json_data=None, response_type='json'):
        return await self._request('POST', url, headers=headers, json_data=json_data, response_type=response_type)

    async def _request(self, method, url, headers=None, json_data=None, response_type='text'):
        domain = url.split('/')[2]
        if domain not in self.circuit_breakers:
            self.circuit_breakers[domain] = CircuitBreaker()

        cb = self.circuit_breakers[domain]

        retries = 5
        for i in range(retries):
            try:
                async with cb:
                    async with aiohttp.ClientSession(headers=headers) as session:
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                        async with session.request(method, url, json=json_data, timeout=15) as response:
                            response.raise_for_status()
                            if response_type == 'json':
                                return await response.json()
                            else:
                                return await response.text()
            except Exception as e:
                logging.warning(f"Attempt {i+1}/{retries} failed for {method} {url}: {e}")
                if i < retries - 1:
                    wait_time = (2 ** i) + random.uniform(0, 1)
                    logging.info(f"Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logging.error(f"All retries failed for {method} {url}")
                    raise

class DataSourceOrchestrator:
    def __init__(self, session):
        self.fetcher = DefensiveFetcher()
        self.db_session = session
        # Gold, Silver, Bronze tiering
        self.adapters: List[BaseAdapterV7] = [
            # --- NEW TIER 1 API ADAPTERS ---
            FanDuelGraphQLAdapterV7(self.fetcher),
            BetfairDataScientistAdapterV7(self.fetcher),
            TwinspiresAdapterV7(self.fetcher),
            # --- EXISTING FOUNDATION ---
            RacingPostAdapterV7(self.fetcher),
            PointsBetAdapterV7(self.fetcher),
            EquibaseAdapterV7(self.fetcher),
        ]

    async def get_races(self) -> List[Race]:
        """
        Iterates through adapters by priority, attempting to fetch races.
        Returns the first successful, non-empty list of races.
        """
        all_races = []
        for adapter in self.adapters:
            adapter_name = adapter.SOURCE_ID
            logging.info(f"Attempting to fetch races from {adapter_name}")
            try:
                # In a real-world scenario, the URL would be dynamic or configured
                # For now, we call fetch_races without arguments where possible
                # or with a default/mock URL.
                if isinstance(adapter, RacingPostAdapterV7):
                    # This adapter needs a specific URL, which we don't have in this context.
                    # We will rely on other adapters for now.
                    logging.warning(f"Skipping {adapter_name} as it requires a specific URL.")
                    continue

                races = await adapter.fetch_races()

                if races:
                    logging.info(f"Successfully fetched {len(races)} races from {adapter_name}")
                    # In a real system, we might aggregate or just return the first success
                    all_races.extend(races)
                    # For now, let's return after the first successful fetch to avoid duplicates
                    return all_races
                else:
                    logging.info(f"No races found from {adapter_name}")

            except Exception as e:
                logging.error(f"Failed to fetch from {adapter_name}: {e}")
                # Here we would update the adapter status in the DB
                # e.g., await self.update_adapter_status(adapter_name, "error")
                continue

        logging.info(f"Harvested a total of {len(all_races)} races from all sources.")
        return all_races

def get_db_session():
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

@celery_app.task(bind=True, max_retries=3)
def run_prediction_cycle(self):
    """The main entry point task for the Prediction Engine."""
    logging.info("Starting prediction cycle...")
    session = None
    try:
        session = get_db_session()
        orchestrator = DataSourceOrchestrator(session)
        races = asyncio.run(orchestrator.get_races())

        logging.info(f"Found {len(races)} races to process.")
        for race in races:
            # Convert dataclass to dict for Celery serialization
            process_race_for_prediction.delay(race.__dict__)

    except SQLAlchemyError as e:
        logging.error("Database error during prediction cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=60)
    except Exception as e:
        logging.error("An unexpected error occurred during prediction cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=60)
    finally:
        if session:
            session.close()

@celery_app.task
def process_race_for_prediction(race_data: dict):
    """Analyzes a single race and saves a prediction if it qualifies."""
    # This task is now designed to be called by the main cycle
    session = get_db_session()
    try:
        # The race data would be a dict here, needs to be reconstructed
        # For now, we'll just log it.
        logging.info(f"Processing race: {race_data.get('track')} R{race_data.get('race_number')}")
        # analyzer = logic.AdvancedPlaceBetAnalyzer() # When implemented
        # analysis = analyzer.analyze(race_data)
        # if analysis.should_bet:
        #     # db_manager.save_prediction(analysis)
        #     pass
    finally:
        session.close()


@celery_app.task(bind=True, max_retries=3)
def run_audit_cycle(self):
    """The main entry point task for the Historian Engine."""
    logging.info("Starting audit cycle...")
    session = None
    try:
        session = get_db_session()
        pending_predictions = session.query(PredictionORM).filter_by(status='pending').all()
        logging.info(f"Found {len(pending_predictions)} pending predictions to audit.")
        for pred in pending_predictions:
            # Check if race time has passed
            # For now, we just queue all pending
            process_race_for_results.delay(pred.race_key)
    except SQLAlchemyError as e:
        logging.error("Database error during audit cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=300)
    except Exception as e:
        logging.error("An unexpected error occurred during audit cycle", extra={"error": str(e)})
        self.retry(exc=e, countdown=300)
    finally:
        if session:
            session.close()


@celery_app.task
def process_race_for_results(race_key: str):
    """Fetches results for a single race and creates an audit record."""
    logging.info(f"Fetching results for {race_key}...")
    # In a real implementation, this would fetch real results and
    # create a real audit record. For now, it's a placeholder.
    pass

# --- V7 Adapters ---

class BaseAdapterV7(ABC):
    def __init__(self, defensive_fetcher: DefensiveFetcher):
        self.fetcher = defensive_fetcher

    @abstractmethod
    async def fetch_races(self) -> List[Race]:
        raise NotImplementedError

class RacingPostAdapterV7(BaseAdapterV7):
    SOURCE_ID = "racingpost"
    BASE_URL = "https://www.racingpost.com" # Example, not used in offline parse

    async def fetch_races(self, url: str) -> List[Race]:
        """Fetches and parses races from a given Racing Post URL."""
        html_content = await self.fetcher.fetch(url)
        if not html_content:
            return []
        return self._parse_races(html_content)

    def _parse_races(self, html_content: str) -> List[Race]:
        """Parses races from the HTML content."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')
        race_data_json = self._extract_race_data_json(html_content)
        if not race_data_json:
            return []

        races = []
        # This logic is transplanted from the legacy adapter and adapted for V7 models
        # It is simplified for this example and would need to be more robust in production.
        race_containers = soup.select('div.RC-meetingDay__race')
        for race_container in race_containers:
            race_id = race_container.get('data-diffusion-race-id')
            track_name = race_data_json.get('location', {}).get('name')

            # --- Full Runner Parsing Logic ---
            runners = []
            runner_rows = race_container.select('div.RC-runnerRow')
            for row in runner_rows:
                if 'RC-runnerRow_disabled' in row.get('class', []):
                    continue

                program_number_span = row.select_one('span.RC-runnerNumber__no')
                program_number = int(program_number_span.text.strip()) if program_number_span else None

                runner_name_a = row.select_one('a.RC-runnerName')
                runner_name = runner_name_a.text.strip() if runner_name_a else "Unknown Runner"

                # V7 Runner model does not include jockey, trainer, or odds.
                # This data is available in the source but will be omitted here.

                runners.append(Runner(
                    name=runner_name,
                    program_number=program_number
                ))

            races.append(Race(
                race_id=race_id,
                track_name=track_name,
                race_number=None, # Not easily available in top-level data
                runners=runners
            ))
        return races

    def _extract_race_data_json(self, html_content: str) -> dict:
        """Extracts the main JSON data blob from the page's script tags."""
        # Corrected the regex to match 'rp_config_.page' instead of 'rp_config_\.page'
        match = re.search(r'rp_config_\.page\s*=\s*({.*?});', html_content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return {}
        return {}

class PointsBetAdapterV7(BaseAdapterV7):
    SOURCE_ID = "pointsbet"
    API_URL = "https://api.au.pointsbet.com/api/v2/racing/races/today"

    async def fetch_races(self) -> List[Race]:
        """Fetches and parses races from the PointsBet API."""
        raw_content = await self.fetcher.fetch(self.API_URL)
        if not raw_content:
            return []
        try:
            json_content = json.loads(raw_content)
        except json.JSONDecodeError:
            logging.error(f"{self.SOURCE_ID}: Failed to decode JSON from response.")
            return []
        return self._parse_races(json_content.get('events', []))

    def _parse_races(self, events: list) -> List[Race]:
        """Parses the JSON response from the PointsBet API."""
        all_races = []
        for event in events:
            try:
                if not event.get('runners') or not event.get('meetingName'):
                    continue

                runners = []
                for runner_data in event.get('runners', []):
                    program_number = runner_data.get('runnerNumber')
                    if not program_number:
                        continue

                    odds_obj = runner_data.get('fixedWinOdds')
                    odds = None
                    if odds_obj:
                        odds = odds_obj.get('price')

                    runners.append(Runner(
                        name=runner_data.get('name', 'Unknown Runner'),
                        program_number=int(program_number),
                        odds=float(odds) if odds else None
                    ))

                if runners:
                    all_races.append(Race(
                        race_id=event.get('key'),
                        track_name=event.get('meetingName'),
                        race_number=event.get('raceNumber'),
                        runners=runners
                    ))
            except (KeyError, TypeError, ValueError) as e:
                logging.warning(f"PointsBetV7: Skipping a malformed event in parse: {e}")
                continue
        return all_races

class EquibaseAdapterV7(BaseAdapterV7):
    SOURCE_ID = "equibase"
    BASE_URL = "http://www.equibase.com"

    async def fetch_races(self) -> List[Race]:
        """
        Fetches all race data for today via a two-step process:
        1. Fetch the main entries page to get the race schedule.
        2. Fetch the detail page for each race to get the runners.
        """
        date_str = date.today().strftime('%m%d%y')
        entries_url = f"{self.BASE_URL}/entries/ENT_{date_str}.html?COUNTRY=USA"

        # Step 1: Fetch and parse the main schedule page
        schedule_html = await self.fetcher.fetch(entries_url)
        if not schedule_html:
            return []

        partial_races, detail_urls = self._parse_race_schedule(schedule_html)

        # Create a mapping from URL to race object to recombine later
        url_to_race_map = {url: race for url, race in zip(detail_urls, partial_races)}

        # Step 2: Fetch all detail pages concurrently using anyio
        detail_pages_html = {}

        async def fetch_and_store(url):
            html = await self.fetcher.fetch(f"{self.BASE_URL}{url}")
            if html:
                detail_pages_html[url] = html

        async with anyio.create_task_group() as tg:
            for url in detail_urls:
                tg.start_soon(fetch_and_store, url)

        # Step 3: Parse runners from detail pages and combine
        final_races = []
        for url, race in url_to_race_map.items():
            detail_html = detail_pages_html.get(url)
            if detail_html:
                runners = self._parse_runners_from_detail_page(detail_html)
                race.runners = runners
            final_races.append(race)

        return final_races

    def _parse_race_schedule(self, html_content: str) -> (List[Race], List[str]):
        """Parses the main entries page to get race info and detail page URLs."""
        if not html_content:
            return [], []

        soup = BeautifulSoup(html_content, 'html.parser')
        partial_races = []
        detail_urls = []

        track_tables = soup.find_all('table', summary=lambda s: s and s.startswith('Track Abbr:'))
        for track_table in track_tables:
            try:
                track_name = track_table.find('tr').find('strong').text.strip()
                for race_row in track_table.find_all('tr', class_='entry'):
                    links = race_row.find_all('a')
                    if len(links) < 2:
                        continue

                    race_number = int(''.join(filter(str.isdigit, links[0].text.strip())))
                    race_id = f"{self.SOURCE_ID}_{track_name.replace(' ', '')}_{date.today().strftime('%Y%m%d')}_R{race_number}"
                    detail_url = links[1]['href']

                    partial_races.append(Race(
                        race_id=race_id, track_name=track_name, race_number=race_number, runners=[]
                    ))
                    detail_urls.append(detail_url)
            except Exception as e:
                logging.warning(f"EquibaseV7: Skipping a malformed schedule table/row: {e}")
                continue
        return partial_races, detail_urls

    def _parse_runners_from_detail_page(self, html_content: str) -> List[Runner]:
        """Parses the race detail page to get a list of runners."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        runners = []
        # Assumption: Runners are in a table with class 'entries'
        runner_rows = soup.select('table.entries tr.entry')
        for row in runner_rows:
            try:
                # Assumption: Program number is in a <strong> tag
                program_number_tag = row.find('strong')
                program_number = int(program_number_tag.text.strip()) if program_number_tag else None

                # Assumption: Runner name is in a <td> with class 'horse'
                runner_name_tag = row.find('td', class_='horse')
                runner_name = runner_name_tag.text.strip() if runner_name_tag else 'Unknown Runner'

                if program_number and runner_name:
                    runners.append(Runner(name=runner_name, program_number=program_number))
            except Exception as e:
                logging.warning(f"EquibaseV7: Skipping a malformed runner row: {e}")
                continue
        return runners


class FanDuelGraphQLAdapterV7(BaseAdapterV7):
    """Adapter for the FanDuel GraphQL API."""
    SOURCE_ID = "fanduel"
    API_URL = "https://sb-prod-df.sportsbook.fanduel.com/api/v2/horse-racing/races"

    async def fetch_races(self) -> List[Race]:
        """Fetches data from the FanDuel GraphQL API."""
        graphql_query = {
            "query": """
                query AllRaces($first: Int!, $next: String) {
                    allRaces(first: $first, after: $next) {
                        edges { node { trackName raceNumber postTime runners { runnerName odds scratched } } }
                    }
                }
            """,
            "variables": {"first": 100}
        }
        try:
            raw_data = await self.fetcher.post(self.API_URL, json_data=graphql_query)
            if not raw_data:
                return []
            return self._parse_races(raw_data)
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to fetch or parse races: {e}")
            return []

    def _parse_races(self, raw_data: dict) -> List[Race]:
        """Parses the JSON response from the GraphQL API."""
        races = []
        race_edges = raw_data.get("data", {}).get("allRaces", {}).get("edges", [])
        if not race_edges:
            return []

        for edge in race_edges:
            node = edge.get("node", {})
            if not node:
                continue

            runners = []
            for runner_data in node.get("runners", []):
                if runner_data.get('scratched'):
                    continue
                runners.append(Runner(
                    name=runner_data.get("runnerName"),
                    odds=self._to_float_odds(runner_data.get("odds")),
                    program_number=None  # Not provided in API
                ))

            post_time = self._to_datetime(node.get("postTime"))
            track_name = node.get('trackName')
            race_number = node.get('raceNumber')

            races.append(Race(
                race_id=f"{self.SOURCE_ID}_{track_name}_{race_number}",
                track_name=track_name,
                race_number=race_number,
                post_time=post_time,
                runners=runners
            ))
        return races

    def _to_float_odds(self, odds_str: Optional[str]) -> Optional[float]:
        if not odds_str or "/" not in odds_str:
            return None
        try:
            num, den = map(int, odds_str.split('/'))
            return (num / den) + 1.0
        except (ValueError, ZeroDivisionError):
            return None

    def _to_datetime(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None


class BetfairDataScientistAdapterV7(BaseAdapterV7):
    """Adapter for the Betfair Data Scientist API (CSV format)."""
    SOURCE_ID = "betfair_data_scientist"
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"

    async def fetch_races(self) -> List[Race]:
        """Fetches and parses data from the Betfair Data Scientist API."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"

        csv_data = await self.fetcher.fetch(url, response_type='text')
        if not csv_data:
            return []
        return self._parse_races(csv_data)

    def _parse_races(self, csv_content: str) -> List[Race]:
        """Parses the CSV content from the API into a list of Race objects."""
        if not csv_content:
            return []

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
                        track_name="Unknown", # Not in this API response
                        race_number=None,
                        runners=[],
                    )

                runner = Runner(
                    name=str(row["selection_id"]), # Using selection_id as name
                    program_number=None, # Not in this API response
                    odds=row["rating"],
                )
                races[race_id].runners.append(runner)

            return list(races.values())
        except Exception as e:
            logging.error(f"{self.SOURCE_ID}: Failed to parse CSV data: {e}")
            return []


class TwinspiresAdapterV7(BaseAdapterV7):
    """Adapter for the TwinSpires website (two-stage scrape)."""
    SOURCE_ID = "twinspires"
    BASE_URL = "https://www.twinspires.com"

    async def fetch_races(self) -> List[Race]:
        """Fetches all race data using a two-stage process."""
        index_url = f"{self.BASE_URL}/adw/todays-tracks?sortOrder=nextUp"
        index_html = await self.fetcher.fetch(index_url, response_type='text')
        if not index_html:
            return []

        detail_links = self._parse_race_links(index_html)
        if not detail_links:
            return []

        detail_pages_html = []
        async def fetch_and_store(link):
            html = await self.fetcher.fetch(link, response_type='text')
            if html:
                detail_pages_html.append(html)

        async with anyio.create_task_group() as tg:
            for link in detail_links:
                tg.start_soon(fetch_and_store, link)

        all_races = []
        for html in detail_pages_html:
            if html:
                try:
                    race = self._parse_single_race_detail(html)
                    if race:
                        all_races.append(race)
                except Exception as e:
                    logging.warning(f"{self.SOURCE_ID}: Skipping a malformed race detail page: {e}")
                    continue
        return all_races

    def _parse_race_links(self, html_content: str) -> List[str]:
        """Parses the index page to find links to all race detail pages."""
        soup = BeautifulSoup(html_content, 'html.parser')
        race_links = []
        for link in soup.find_all('a', href=lambda h: h and '/races/' in h and '/results/' not in h):
            race_links.append(self.BASE_URL + link['href'])
        return list(set(race_links)) # Use set to remove duplicate links

    def _parse_single_race_detail(self, html: str) -> Optional[Race]:
        """Parses a single race detail HTML page."""
        soup = BeautifulSoup(html, 'html.parser')

        header = soup.find('div', class_='race-title')
        if not header: return None

        track_name = header.find('a').text.strip()
        race_number_text = header.find('strong').text
        race_number = int(''.join(filter(str.isdigit, race_number_text)))

        runners = []
        program = soup.find('div', id='program')
        if not program: return None

        for i, runner_row in enumerate(program.find_all('div', class_='runner-wrapper')):
            name_tag = runner_row.find('div', class_='runner-name')
            if not name_tag: continue
            name = name_tag.text.strip()

            odds_span = runner_row.find('span', class_='odds')
            odds_str = odds_span.text.strip() if odds_span else None

            if not odds_str: continue

            try:
                if '/' in odds_str:
                    num, den = map(int, odds_str.split('/'))
                    odds = (num / den) + 1.0 if den != 0 else None
                else:
                    odds = float(odds_str) + 1.0

                if odds is not None:
                    runners.append(Runner(
                        name=name,
                        odds=odds,
                        program_number=i + 1
                    ))
            except (ValueError, TypeError):
                continue

        if not runners:
            return None

        return Race(
            race_id=f"{self.SOURCE_ID}_{track_name.replace(' ', '')}_{race_number}",
            track_name=track_name,
            race_number=race_number,
            runners=runners
        )
