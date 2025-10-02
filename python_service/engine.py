# python_service/engine.py

import logging
import time
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

from .adapters.betfair_adapter import BetfairAdapter
from .adapters.tvg_adapter import TVGAdapter
from .adapters.racing_and_sports_adapter import RacingAndSportsAdapter
from .adapters.pointsbet_adapter import PointsBetAdapter

class DefensiveFetcher:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self._rate_limiters: Dict[str, float] = {}

    def get(self, url: str, headers: dict, source_id: str, timeout: int = 15) -> dict:
        if self._is_circuit_open(source_id):
            msg = f"Circuit for {source_id} is open. Skipping request."
            return {'success': False, 'error': 'CircuitBreakerOpen', 'message': msg}
        self._apply_rate_limit(source_id)
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            self._record_success(source_id)
            return {'success': True, 'data': response.json()}
        except requests.exceptions.Timeout as e:
            self._record_failure(source_id)
            return {'success': False, 'error': 'Timeout', 'message': str(e)}
        except requests.exceptions.HTTPError as e:
            self._record_failure(source_id)
            return {'success': False, 'error': 'HTTPError', 'status_code': e.response.status_code, 'message': str(e)}
        except requests.RequestException as e:
            self._record_failure(source_id)
            return {'success': False, 'error': 'RequestException', 'message': str(e)}

    def _is_circuit_open(self, source_id: str) -> bool:
        breaker = self._circuit_breakers.get(source_id, {'failures': 0, 'open_until': 0})
        return time.time() < breaker['open_until']

    def _record_failure(self, source_id: str):
        breaker = self._circuit_breakers.setdefault(source_id, {'failures': 0, 'open_until': 0})
        breaker['failures'] += 1
        if breaker['failures'] >= 3:
            breaker['open_until'] = time.time() + 60

    def _record_success(self, source_id: str):
        self._circuit_breakers.pop(source_id, None)

    def _apply_rate_limit(self, source_id: str, delay: float = 1.0):
        last_call = self._rate_limiters.get(source_id, 0)
        elapsed = time.time() - last_call
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._rate_limiters[source_id] = time.time()

class RaceScorer:
    def __init__(self):
        self.qualification_score = 75.0

    def score_race(self, race) -> Dict[str, Any]:
        score = 50.0
        is_qualified = score >= self.qualification_score
        # In a real system, we'd merge the score into the race object
        return {'race': race, 'score': score, 'is_qualified': is_qualified}

class EngineManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fetcher = DefensiveFetcher()
        self.scorer = RaceScorer()
        self._adapters = {}
        self._cache = {}
        self._cache_ttl = timedelta(seconds=60)
        self.last_run_failures: List[Dict[str, Any]] = []
        self._initialize_adapters()

    def _initialize_adapters(self):
        adapter_classes = {
            'betfair': BetfairAdapter, 'tvg': TVGAdapter,
            'racing_and_sports': RacingAndSportsAdapter, 'pointsbet': PointsBetAdapter
        }
        for name, AdapterClass in adapter_classes.items():
            try: self._adapters[name] = AdapterClass(self.fetcher)
            except Exception as e: self.logger.error(f"Failed to initialize {name} adapter: {e}")

    def fetch_and_process_races(self):
        cache_key = "processed_races"
        if self._is_cache_valid(cache_key): return self._cache[cache_key][0]

        self.last_run_failures = []
        raw_races = []
        races_by_adapter = {}
        with ThreadPoolExecutor(max_workers=len(self._adapters)) as executor:
            future_to_adapter = {executor.submit(adapter.fetch_races): name for name, adapter in self._adapters.items()}
            for future in as_completed(future_to_adapter):
                adapter_name = future_to_adapter[future]
                try:
                    result = future.result(timeout=20)
                    if result['success']:
                        races_by_adapter[adapter_name] = result['data']
                        raw_races.extend(result['data'])
                    else:
                        races_by_adapter[adapter_name] = []
                        # Correctly handle the error dictionary from DefensiveFetcher
                        failure_report = result
                        failure_report['adapter'] = adapter_name
                        self.last_run_failures.append(failure_report)
                except Exception as e:
                    races_by_adapter[adapter_name] = []
                    self.last_run_failures.append({'adapter': adapter_name, 'error': 'ExecutionException', 'message': str(e)})

        processed_races = raw_races
        scored_races = [self.scorer.score_race(race) for race in processed_races]
        qualified_races = [r for r in scored_races if r['is_qualified']]

        funnel_stats = {
            'races_fetched_by_source': {name: len(races) for name, races in races_by_adapter.items()},
            'total_races_fetched': sum(len(races) for races in races_by_adapter.values()),
            'races_after_deduplication': len(processed_races),
            'races_after_scoring': len(scored_races),
            'qualified_races': len(qualified_races)
        }
        self._cache['funnel_stats'] = (funnel_stats, datetime.now())
        self._cache[cache_key] = (qualified_races, datetime.now())
        return qualified_races

    def get_funnel_statistics(self) -> Dict[str, Any]:
        if self._is_cache_valid("funnel_stats"): return self._cache["funnel_stats"][0]
        return {"status": "stale", "message": "Funnel data is being generated."}

    def get_dashboard_summary(self) -> Dict[str, Any]:
        if not self._is_cache_valid("processed_races"):
            return {"status": "stale", "message": "Data is being fetched.", "fetcher_failures": self.last_run_failures}
        races, timestamp = self._cache["processed_races"]
        return {
            "status": "ok",
            "last_updated": timestamp.isoformat(),
            "total_qualified_races": len(races),
            "fetcher_failures": self.last_run_failures
        }

    def get_adapter_status(self, adapter_name):
        if adapter_name not in self._adapters: return None
        return {'name': adapter_name, 'status': 'healthy' if not self.fetcher._is_circuit_open(adapter_name) else 'degraded'}

    def _is_cache_valid(self, key):
        if key not in self._cache: return False
        _, timestamp = self._cache[key]
        return (datetime.now() - timestamp) < self._cache_ttl