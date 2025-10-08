# python_service/adapter_anthology.py
# This file contains the COMPLETE, VERBATIM source code for all working adapters.

import asyncio, structlog, httpx, re, json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag
from decimal import Decimal, InvalidOperation
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, AsyncRetrying

from .models import Race, Runner, OddsData
from .config import get_settings

log = structlog.get_logger(__name__)

# --- UTILITIES ---
def _clean_text(text: Optional[str]) -> Optional[str]:
    return ' '.join(text.strip().split()) if text else None

def parse_odds(odds: Any) -> float:
    if isinstance(odds, (int, float)): return float(odds)
    if isinstance(odds, str):
        try:
            if "/" in odds:
                n, d = map(int, odds.split('/'))
                return 1.0 + (n / d) if d != 0 else 999.0
            if odds.lower() == 'evens': return 2.0
            return float(odds)
        except (ValueError, TypeError): return 999.0
    return 999.0

# --- BASE ADAPTER ---
class BaseAdapter:
    BASE_URL: str = ""
    SOURCE_NAME: str = ""
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_races(self) -> List[Race]:
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_races()")

    async def make_request(self, method: str, url: str, **kwargs) -> Optional[Any]:
        retryer = AsyncRetrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
        try:
            async for attempt in retryer:
                with attempt:
                    full_url = url if url.startswith('http') else f"{self.BASE_URL}{url}"
                    response = await self.client.request(method, full_url, **kwargs)
                    response.raise_for_status()
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return response.text
        except Exception as e:
            log.error(f"Request failed for {self.SOURCE_NAME}", url=full_url, error=str(e))
            return None

# --- ADAPTER ANTHOLOGY ---

class AtTheRacesAdapter(BaseAdapter):
    BASE_URL = "https://www.attheraces.com"
    SOURCE_NAME = "AtTheRaces"

    async def get_races(self) -> List[Race]:
        race_links = await self._get_race_links()
        if not race_links: return []
        tasks = [self._fetch_and_parse_race(link) for link in race_links]
        races = [race for race in await asyncio.gather(*tasks) if race]
        return races

    async def _get_race_links(self) -> List[str]:
        response_html = await self.make_request('GET', '/racecards')
        if not response_html: return []
        soup = BeautifulSoup(response_html, "html.parser")
        links = {a['href'] for a in soup.select("a.race-time-link[href]")}
        return [f"{self.BASE_URL}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str) -> Optional[Race]:
        try:
            response_html = await self.make_request('GET', url)
            if not response_html: return None
            soup = BeautifulSoup(response_html, "html.parser")
            header_text = _clean_text(soup.select_one("h1.heading-racecard-title").get_text()).split("|")
            track_name, race_time = [p.strip() for p in header_text[:2]]
            active_link = soup.select_one("a.race-time-link.active")
            all_links_container = active_link.find_parent("div", "races")
            all_links = all_links_container.select("a.race-time-link")
            race_number = all_links.index(active_link) + 1
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time}", "%Y-%m-%d %H:%M")
            runners = [self._parse_runner(row) for row in soup.select("div.card-horse")]
            return Race(id=f"atr_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}", venue=track_name, race_number=race_number, start_time=start_time, runners=[r for r in runners if r], source=self.SOURCE_NAME, race_url=url)
        except Exception: return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("h3.horse-name a").get_text())
            num_str = _clean_text(row.select_one("span.horse-number").get_text())
            number = int(''.join(filter(str.isdigit, num_str)))
            odds_str = _clean_text(row.select_one("button.best-odds").get_text())
            win_odds = Decimal(str(parse_odds(odds_str))) if odds_str else None
            odds_data = {self.SOURCE_NAME: OddsData(win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now())} if win_odds and win_odds < 999 else {}
            return Runner(number=number, name=name, odds=odds_data)
        except: return None

class BetfairAdapter(BaseAdapter):
    BASE_URL = "https://api.betfair.com/exchange/betting/rest/v1.0/"
    SOURCE_NAME = "BetfairExchange"
    session_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

    async def get_races(self) -> List[Race]:
        settings = get_settings()
        if not all([settings.BETFAIR_APP_KEY, settings.BETFAIR_USERNAME, settings.BETFAIR_PASSWORD]):
            log.warning("Betfair credentials not configured. Skipping.", adapter=self.SOURCE_NAME)
            return []
        await self._authenticate(settings)
        if not self.session_token: return []
        headers = {"X-Application": settings.BETFAIR_APP_KEY, "X-Authentication": self.session_token, "Content-Type": "application/json"}
        date_str = datetime.now().strftime('%Y-%m-%d')
        market_filter = {"eventTypeIds": ["7"], "marketTypeCodes": ["WIN"], "marketStartTime": {"from": f"{date_str}T00:00:00Z", "to": f"{date_str}T23:59:59Z"}}
        market_catalogue = await self.make_request('POST', 'listMarketCatalogue/', headers=headers, json={"filter": market_filter, "maxResults": 1000, "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]})
        if not market_catalogue: return []
        return [self._parse_race(market) for market in market_catalogue]

    async def _authenticate(self, settings):
        if self.session_token and self.token_expiry and self.token_expiry > (datetime.now() + timedelta(minutes=5)): return
        auth_url = "https://identitysso.betfair.com/api/login"
        headers = {'X-Application': settings.BETFAIR_APP_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'username={settings.BETFAIR_USERNAME}&password={settings.BETFAIR_PASSWORD}'
        try:
            response = await self.client.post(auth_url, headers=headers, content=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'SUCCESS':
                self.session_token = data.get('token')
                self.token_expiry = datetime.now() + timedelta(hours=3)
            else:
                log.error("Betfair authentication failed", error=data.get('error'))
                self.session_token = None
        except Exception as e:
            log.error("Betfair authentication exception", error=e)
            self.session_token = None

    def _parse_race(self, market: Dict[str, Any]) -> Race:
        race_number = self._extract_race_number(market.get('marketName'))
        runners = [Runner(number=rd.get('sortPriority', 99), name=rd['runnerName']) for rd in market.get('runners', [])]
        return Race(id=f"bf_{market['marketId']}", venue=market['event']['venue'], race_number=race_number, start_time=datetime.fromisoformat(market['marketStartTime'].replace('Z', '+00:00')), runners=runners, source=self.SOURCE_NAME, race_name=market.get('marketName'))

    def _extract_race_number(self, name: Optional[str]) -> int:
        if not name: return 1
        match = re.search(r'R(\d{1,2})', name)
        return int(match.group(1)) if match else 1

class BetfairGreyhoundAdapter(BetfairAdapter):
    SOURCE_NAME = "BetfairGreyhound"

    async def get_races(self) -> List[Race]:
        settings = get_settings()
        if not all([settings.BETFAIR_APP_KEY, settings.BETFAIR_USERNAME, settings.BETFAIR_PASSWORD]): return []
        await self._authenticate(settings)
        if not self.session_token: return []
        headers = {"X-Application": settings.BETFAIR_APP_KEY, "X-Authentication": self.session_token, "Content-Type": "application/json"}
        date_str = datetime.now().strftime('%Y-%m-%d')
        market_filter = {"eventTypeIds": ["4339"], "marketTypeCodes": ["WIN"], "marketStartTime": {"from": f"{date_str}T00:00:00Z", "to": f"{date_str}T23:59:59Z"}}
        market_catalogue = await self.make_request('POST', 'listMarketCatalogue/', headers=headers, json={"filter": market_filter, "maxResults": 1000, "marketProjection": ["EVENT", "RUNNER_DESCRIPTION"]})
        if not market_catalogue: return []
        races = [super()._parse_race(market) for market in market_catalogue]
        for race in races:
            race.id = f"bfg_{race.id.split('_')[1]}"
            race.source = self.SOURCE_NAME
        return races

class HarnessAdapter(BaseAdapter):
    BASE_URL = "https://data.ustrotting.com/"
    SOURCE_NAME = "Harness Racing (USTA)"

    async def get_races(self) -> List[Race]:
        date_str = datetime.now().strftime('%Y-%m-%d')
        endpoint = f"api/racenet/racing/card/{date_str}"
        response_json = await self.make_request('GET', endpoint)
        if not response_json or "meetings" not in response_json: return []
        return self._parse_meetings(response_json["meetings"])

    def _parse_meetings(self, meetings: List[Dict[str, Any]]) -> List[Race]:
        all_races = []
        for meeting in meetings:
            venue = meeting.get("trackName", "Unknown Venue")
            for race_data in meeting.get("races", []):
                try:
                    if not race_data.get("runners"): continue
                    all_races.append(Race(id=f"usta_{race_data['raceId']}", venue=venue, race_number=race_data["raceNumber"], start_time=datetime.fromisoformat(race_data["startTime"].replace("Z", "+00:00")), runners=self._parse_runners(race_data["runners"]), source=self.SOURCE_NAME))
                except (ValidationError, KeyError) as e:
                    log.error("HarnessAdapter: Error parsing race", error=e, race_data=race_data)
        return all_races

    def _parse_runners(self, runners_data: List[Dict[str, Any]]) -> List[Runner]:
        runners = []
        for runner_data in runners_data:
            try:
                runner_number = runner_data.get('postPosition')
                if not runner_number: continue
                odds_data = {}
                win_odds_str = runner_data.get("morningLineOdds")
                if win_odds_str:
                    if '/' not in win_odds_str: win_odds_str = f"{win_odds_str}/1"
                    parsed_float = parse_odds(win_odds_str)
                    if parsed_float < 999.0: odds_data[self.SOURCE_NAME] = OddsData(win=Decimal(str(parsed_float)), source=self.SOURCE_NAME, last_updated=datetime.now())
                runners.append(Runner(number=runner_number, name=runner_data["horseName"], scratched=runner_data.get("scratched", False), odds=odds_data))
            except (KeyError, ValidationError) as e:
                log.error("HarnessAdapter: Error parsing runner", error=e, runner_data=runner_data)
        return runners

class RacingAndSportsAdapter(BaseAdapter):
    BASE_URL = "https://api.racingandsports.com.au/"
    SOURCE_NAME = "Racing and Sports"

    async def get_races(self) -> List[Race]:
        settings = get_settings()
        api_token = settings.RACING_AND_SPORTS_TOKEN
        if not api_token: return []
        date_str = datetime.now().strftime('%Y-%m-%d')
        headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
        params = {"date": date_str, "jurisdiction": "AUS"}
        meetings_data = await self.make_request('GET', "v1/racing/meetings", headers=headers, params=params)
        if not meetings_data or not meetings_data.get('meetings'): return []
        all_races = []
        for meeting in meetings_data['meetings']:
            for race_summary in meeting.get('races', []):
                try: all_races.append(self._parse_ras_race(meeting, race_summary))
                except Exception as e: log.error("RacingAndSportsAdapter: Failed to parse race", error=e)
        return all_races

    def _parse_ras_race(self, meeting: Dict[str, Any], race: Dict[str, Any]) -> Race:
        runners = [Runner(number=rd.get('runnerNumber'), name=rd.get('horseName', 'Unknown'), scratched=rd.get('isScratched', False)) for rd in race.get('runners', [])]
        return Race(id=f"ras_{race.get('raceId')}", venue=meeting.get('venueName', 'Unknown Venue'), race_number=race.get('raceNumber'), start_time=datetime.fromisoformat(race.get('startTime')), runners=runners, source=self.SOURCE_NAME)

class RacingAndSportsGreyhoundAdapter(RacingAndSportsAdapter):
    SOURCE_NAME = "Racing and Sports Greyhound"

    async def get_races(self) -> List[Race]:
        settings = get_settings()
        api_token = settings.RACING_AND_SPORTS_TOKEN
        if not api_token: return []
        date_str = datetime.now().strftime('%Y-%m-%d')
        headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}
        params = {"date": date_str, "jurisdiction": "AUS"}
        meetings_data = await self.make_request('GET', "v1/greyhound/meetings", headers=headers, params=params)
        if not meetings_data or not meetings_data.get('meetings'): return []
        all_races = []
        for meeting in meetings_data['meetings']:
            for race_summary in meeting.get('races', []):
                try:
                    race = self._parse_ras_race(meeting, race_summary)
                    race.id = f"rasg_{race_summary.get('raceId')}"
                    race.source = self.SOURCE_NAME
                    all_races.append(race)
                except Exception as e: log.error("RacingAndSportsGreyhoundAdapter: Failed to parse race", error=e)
        return all_races

class SportingLifeAdapter(BaseAdapter):
    BASE_URL = "https://www.sportinglife.com"
    SOURCE_NAME = "SportingLife"

    async def get_races(self) -> List[Race]:
        race_links = await self._get_race_links()
        if not race_links: return []
        tasks = [self._fetch_and_parse_race(link) for link in race_links]
        return [race for race in await asyncio.gather(*tasks) if race]

    async def _get_race_links(self) -> List[str]:
        response_html = await self.make_request('GET', '/horse-racing/racecards')
        if not response_html: return []
        soup = BeautifulSoup(response_html, "html.parser")
        links = {a['href'] for a in soup.select("a.hr-race-card-meeting__race-link[href]")}
        return [f"{self.BASE_URL}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str) -> Optional[Race]:
        try:
            response_html = await self.make_request('GET', url)
            if not response_html: return None
            soup = BeautifulSoup(response_html, "html.parser")
            track_name = _clean_text(soup.select_one("a.hr-race-header-course-name__link").get_text())
            race_time_str = _clean_text(soup.select_one("span.hr-race-header-time__time").get_text())
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
            active_link = soup.select_one("a.hr-race-header-navigation-link--active")
            all_links = soup.select("a.hr-race-header-navigation-link")
            race_number = all_links.index(active_link) + 1 if active_link in all_links else 1
            runners = [self._parse_runner(row) for row in soup.select("div.hr-racing-runner-card")]
            return Race(id=f"sl_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}", venue=track_name, race_number=race_number, start_time=start_time, runners=[r for r in runners if r], source=self.SOURCE_NAME, race_url=url)
        except Exception as e:
            log.error("SportingLifeAdapter: Failed to parse race page", url=url, error=e)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("a.hr-racing-runner-horse-name").get_text())
            num_str = _clean_text(row.select_one("span.hr-racing-runner-saddle-cloth-no").get_text())
            number = int(''.join(filter(str.isdigit, num_str)))
            odds_str = _clean_text(row.select_one("span.hr-racing-runner-odds").get_text())
            win_odds = Decimal(str(parse_odds(odds_str))) if odds_str else None
            odds_data = {self.SOURCE_NAME: OddsData(win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now())} if win_odds and win_odds < 999 else {}
            return Runner(number=number, name=name, odds=odds_data)
        except: return None

class TimeformAdapter(BaseAdapter):
    BASE_URL = "https://www.timeform.com"
    SOURCE_NAME = "Timeform"

    async def get_races(self) -> List[Race]:
        race_links = await self._get_race_links()
        if not race_links: return []
        tasks = [self._fetch_and_parse_race(link) for link in race_links]
        return [race for race in await asyncio.gather(*tasks) if race]

    async def _get_race_links(self) -> List[str]:
        response_html = await self.make_request('GET', '/horse-racing/racecards')
        if not response_html: return []
        soup = BeautifulSoup(response_html, "html.parser")
        links = {a['href'] for a in soup.select("a.rp-racecard-off-link[href]")}
        return [f"{self.BASE_URL}{link}" for link in links]

    async def _fetch_and_parse_race(self, url: str) -> Optional[Race]:
        try:
            response_html = await self.make_request('GET', url)
            if not response_html: return None
            soup = BeautifulSoup(response_html, "html.parser")
            track_name = _clean_text(soup.select_one("h1.rp-raceTimeCourseName_name").get_text())
            race_time_str = _clean_text(soup.select_one("span.rp-raceTimeCourseName_time").get_text())
            start_time = datetime.strptime(f"{datetime.now().date()} {race_time_str}", "%Y-%m-%d %H:%M")
            all_times = [_clean_text(a.get_text()) for a in soup.select('a.rp-racecard-off-link')]
            race_number = all_times.index(race_time_str) + 1 if race_time_str in all_times else 1
            runners = [self._parse_runner(row) for row in soup.select("div.rp-horseTable_mainRow")]
            return Race(id=f"tf_{track_name.replace(' ', '')}_{start_time.strftime('%Y%m%d')}_R{race_number}", venue=track_name, race_number=race_number, start_time=start_time, runners=[r for r in runners if r], source=self.SOURCE_NAME, race_url=url)
        except Exception as e:
            log.error("TimeformAdapter: Failed to parse race page", url=url, error=e)
            return None

    def _parse_runner(self, row: Tag) -> Optional[Runner]:
        try:
            name = _clean_text(row.select_one("a.rp-horseTable_horse-name").get_text())
            num_str = _clean_text(row.select_one("span.rp-horseTable_horse-number").get_text()).strip("()")
            number = int(''.join(filter(str.isdigit, num_str)))
            odds_str = _clean_text(row.select_one("button.rp-bet-placer-btn__odds").get_text())
            win_odds = Decimal(str(parse_odds(odds_str))) if odds_str else None
            odds_data = {self.SOURCE_NAME: OddsData(win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now())} if win_odds and win_odds < 999 else {}
            return Runner(number=number, name=name, odds=odds_data)
        except: return None

class TVGAdapter(BaseAdapter):
    BASE_URL = "https://api.tvg.com/v3/"
    SOURCE_NAME = "TVG"

    def _parse_program_number(self, program_str: str) -> int:
        return int(''.join(filter(str.isdigit, program_str))) if program_str else 99

    async def get_races(self) -> List[Race]:
        settings = get_settings()
        api_key = settings.TVG_API_KEY
        if not api_key: return []
        date_str = datetime.now().strftime('%Y-%m-%d')
        headers = {"Accept": "application/json", "X-API-Key": api_key}
        params = {"date": date_str, "country": "US"}
        tracks_response = await self.make_request('GET', "tracks", headers=headers, params=params)
        if not tracks_response or 'tracks' not in tracks_response: return []
        all_races = []
        for track in tracks_response['tracks']:
            try:
                races_url = f"tracks/{track['code']}/races"
                races_response = await self.make_request('GET', races_url, headers=headers, params={"date": date_str})
                if not races_response: continue
                for race_summary in races_response.get('races', []):
                    race_detail_url = f"tracks/{track['code']}/races/{race_summary['number']}"
                    race_detail = await self.make_request('GET', race_detail_url, headers=headers)
                    if race_detail: all_races.append(self._parse_tvg_race(track, race_detail))
            except httpx.HTTPError as e:
                log.error("TVGAdapter: Failed to process track", track_name=track.get('name'), error=str(e))
        return all_races

    def _parse_tvg_race(self, track: Dict[str, Any], race_data: Dict[str, Any]) -> Race:
        runners = []
        for runner_data in race_data.get('runners', []):
            if not runner_data.get('scratched'):
                odds_str = runner_data.get('odds', {}).get('current') or runner_data.get('odds', {}).get('morningLine')
                win_odds = self._parse_tvg_odds(odds_str)
                odds_data = {self.SOURCE_NAME: OddsData(win=win_odds, source=self.SOURCE_NAME, last_updated=datetime.now())} if win_odds else {}
                runners.append(Runner(number=self._parse_program_number(runner_data.get('programNumber')), name=runner_data.get('horseName', 'Unknown Runner'), scratched=False, odds=odds_data))
        return Race(id=f"tvg_{track.get('code', 'UNK').lower()}_{race_data['postTime'].split('T')[0]}_R{race_data['number']}", venue=track.get('name', 'Unknown Venue'), race_number=race_data.get('number'), start_time=datetime.fromisoformat(race_data.get('postTime')), runners=runners, source=self.SOURCE_NAME)

    def _parse_tvg_odds(self, odds_string: str) -> Optional[Decimal]:
        if not odds_string or odds_string == "SCR": return None
        try:
            parsed_float = parse_odds(odds_string)
            if parsed_float >= 999.0: return None
            return Decimal(str(parsed_float))
        except (ValueError, InvalidOperation): return None