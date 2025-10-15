# Fortuna Faucet - Comprehensive Pseudocode Blueprint

---

## GLOBAL OVERVIEW

```
SYSTEM FortuneFaucet:
  PURPOSE:
    - Collect global horse/greyhound/harness racing data.
    - Normalize, analyze, and surface betting opportunities.
    - Expose intelligence via API + UI command deck.
  ARCHITECTURE:
    - Pillar1: Python Async Backend (fast data orchestration).
    - Pillar2: TypeScript/Next.js Frontend (interactive dashboard).
  SUPPORTING ARTIFACTS:
    - Streamlit utility dashboard.
    - Chart scraping pipeline.
    - Windows automation scripts.
    - Extensive documentation + roadmaps.
```

---

## BACKEND CORE (python_service)

### Configuration & Logging

```
MODULE config.Settings:
  LOAD environment variables via pydantic-settings.
  KEY FIELDS:
    API_KEY (mandatory security token)
    BETFAIR credentials (optional but required for adapters)
    TVG, RACING_AND_SPORTS, POINTSBET tokens (optional)
    GREYHOUND_API_URL, THE_RACING_API_KEY (optional)
    REDIS_URL default "redis://localhost"
    ALLOWED_ORIGINS default [local dev origins]
  EXPORT get_settings() with lru_cache for singleton behavior.

MODULE logging_config.configure_logging():
  SETUP structlog + logging.basicConfig
  FORMAT logs as JSON with timestamp, level, logger name, stack info.
```

### Data Contracts

```
MODULE models:
  DEFINE OddsData:
    FIELDS: win Decimal>1, source str, last_updated datetime
    VALIDATE win > 1 when present.

  DEFINE Runner:
    FIELDS: number (1-99), name <=100 chars, scratched flag (default False),
            selection_id optional, odds dict[provider->OddsData],
            jockey/trainer optional metadata.

  DEFINE Race:
    FIELDS: id str, venue str, race_number (1-20),
            start_time datetime, runners list[Runner],
            source str, optional qualification_score, race_name, distance.
    VALIDATE unique runner numbers per race.

  DEFINE SourceInfo:
    name, status ("SUCCESS"/"FAILED"), races_fetched count,
    optional error_message, fetch_duration float.

  DEFINE FetchMetadata:
    fetch_time datetime, sources_queried list[str],
    sources_successful int, total_races int.

  DEFINE AggregatedResponse:
    date date, races list[Race], sources list[SourceInfo],
    metadata FetchMetadata.

  DEFINE QualifiedRacesResponse:
    criteria dict[str,Any], races list[Race].
```

### Adapter Framework

```
ABSTRACT BaseAdapter(source_name, base_url, timeout=20, max_retries=3):
  PROVIDES async fetch_races(date, http_client) -> Dict
    (implemented by subclasses).
  PROVIDES make_request(http_client, method, url, **kwargs):
    - Compose full URL when relative.
    - Wrap request with tenacity AsyncRetrying (max_retries, exponential backoff).
    - Log attempts; on success return response.json().
    - On retry exhaustion log error and return None.

  PROVIDES get_status() -> {"adapter_name": source_name, "status": "OK"}.
  PROVIDES _format_response(races, start_time, is_success, error_message):
    - Compute fetch_duration.
    - Package races list + source_info block.
```

### Adapter Inventory (python_service/adapters)

_For each source, implement fetch logic, parse HTML/JSON, convert to Race/Runner models, leverage parse_odds utility._

```
UTILITY parse_odds(odds_input):
  HANDLE ints/floats directly.
  HANDLE fractional strings "num/den" => 1 + num/den.
  HANDLE "evens"/"evs" => 2.0.
  FALLBACK to float parse else return 999.0 sentinel.

MIXIN BetfairAuthMixin:
  MAINTAIN session_token + token_expiry.
  _authenticate(http_client):
    IF cached token valid beyond +5min -> reuse.
    ELSE POST to Betfair identity endpoint with credentials.
    - On success store token + expiry (3 hours).
    - On failure raise ConnectionError.

ADAPTER BetfairAdapter(BetfairAuthMixin, BaseAdapter):
  SOURCE "BetfairExchange", base_url Betfair REST.
  fetch_races(date):
    - Authenticate.
    - Build market_filter for eventTypeId "7" (horse racing).
    - POST listMarketCatalogue with WIN markets in date window.
    - If empty -> success with error_message.
    - Else parse catalogue into races via _parse_race.
  _parse_race:
    - Build Runner for each runnerName, selectionId, sortPriority.
    - Race ID "bf_{marketId}", venue event.venue, race_number via regex "Rxx".
    - start_time from ISO string.
  get_live_odds_for_market(market_id):
    - Authenticate, POST listMarketBook with EX_TRADED price data.
    - Extract lastPriceTraded for ACTIVE runners into Decimal map.
    - Return selectionId->Decimal.

ADAPTER BetfairGreyhoundAdapter:
  IDENTICAL structure; eventTypeId "4339"; Race ID prefix "bfg_".

ADAPTER TVGAdapter:
  REQUIRE TVG_API_KEY.
  fetch_races:
    - GET tracks for date (country US).
    - For each track, GET races summary, then detail per race.
    - Parse to Race with _parse_tvg_race (skip scratched).
  _parse_tvg_race:
    - Program numbers sanitized via helper (strip letters).
    - Extract odds via parse_odds (current or morning line).
    - Compose Race ID with track code + date + race number.

ADAPTER RacingAndSportsAdapter:
  REQUIRE token; on missing return FAILED status.
  fetch_races:
    - GET v1/racing/meetings with date & jurisdiction AUS.
    - Iterate meetings/races, parse to Race via _parse_ras_race.
  _parse_ras_race:
    - Runners with runnerNumber, horseName, scratched flag.
    - start_time iso parse.

ADAPTER RacingAndSportsGreyhoundAdapter:
  Similar to above but endpoint v1/greyhound/meetings, Race prefix "rasg_".

ADAPTER AtTheRacesAdapter:
  Scrape https://www.attheraces.com.
  fetch_races:
    - GET /racecards; parse meeting links.
    - For each link -> fetch, parse track/time, race_number via active nav.
    - Build Race with start_time based on current date + race time (no timezone).
    - _parse_runner: extract horse number, name, best odds button -> parse to Decimal.

ADAPTER SportingLifeAdapter:
  Scrape sportinglife.com racecards.
  Similar approach: gather race links, parse track/time, nav for race_number, runners via cards.

ADAPTER TimeformAdapter:
  Scrape timeform.com racecards.
  Collect links, parse race page, determine race number via list of times, parse runner rows.

ADAPTER HarnessAdapter:
  GET https://data.ustrotting.com/api/racenet/racing/card/{date}.
  Parse meetings -> races -> runners (postPosition).
  Convert morningLineOdds (if not fractional, append "/1"). Parse to Decimal.

ADAPTER GreyhoundAdapter:
  Requires GREYHOUND_API_URL or raise ValueError.
  fetch_races:
    - GET v1/cards/{date}.
    - Parse cards -> races -> runners (filter scratched). Convert odds.win decimals >1 to OddsData.

ADAPTER GbgbApiAdapter:
  GET https://api.gbgb.org.uk/api/results/meeting/{date}.
  Parse meetings/races/traps.
  Race start_time from iso (replace 'Z' with +00:00). Distance appended as string.
  Runners: parse sp fractional odds via parse_odds; assign OddsData.

ADAPTER TheRacingApiAdapter:
  Requires THE_RACING_API_KEY.
  fetch_races:
    - GET racecards?date={date}&course=all&region=gb,ire.
    - Parse racecards -> Race entries (race_id prefix "tra_").
    - Runners: use odds list first entry's odds_decimal -> Decimal.

ADAPTER OddscheckerAdapter:
  Scrape oddschecker horse racing.
  fetch_races:
    - GET /horse-racing -> meeting links.
    - For each meeting fetch race links, then parse table rows -> Runners with odds.
  Race result _format_response dumps Race models as dicts (model_dump).

ADAPTER PointsBetGreyhoundAdapter:
  Placeholder (non-functional) -> returns SUCCESS with error message.

ADAPTER BrisnetAdapter, DRFAdapter, EquibaseAdapter, FanDuelAdapter,
        HorseRacingNationAdapter, NYRABetsAdapter, PuntersAdapter,
        RacingPostAdapter, RacingTVAdapter, TabAdapter, TwinSpiresAdapter,
        XpressbetAdapter, TemplateAdapter:
  Stubs returning empty responses with Not Implemented notice.
```

### Analyzer Layer

```
MODULE analyzer:
  FUNCTION _get_best_win_odds(runner):
    - Pull min win odds from runner.odds values < 999.
    - Return Decimal or None.

  ABSTRACT BaseAnalyzer:
    - qualify_races(races) -> Dict (implemented by concrete analyzers).

  CLASS TrifectaAnalyzer(BaseAnalyzer):
    PARAMETERS: max_field_size=10, min_favorite_odds=2.5, min_second_favorite_odds=4.0 (Decimal).
    METHOD qualify_races(races):
      - For each race compute score via _evaluate_race.
      - Filter races with scores -> assign race.qualification_score.
      - Sort descending by score.
      - Return {"criteria": {params}, "races": qualified_list}.
    METHOD _evaluate_race(race):
      - Filter non-scratched runners.
      - Collect best odds for each runner; require >=2.
      - Sort by odds ascending -> favorite, second favorite.
      - Apply filters:
          field_size <= max_field_size,
          favorite_odds >= min_favorite_odds,
          second_favorite_odds >= min_second_favorite_odds.
      - Compute field_score = (max_field_size - field_size)/max_field_size.
      - Normalize fav/second odds scores (cap 10/15).
      - Weighted combination (field 0.3, odds 0.7).
      - Return final_score *100 rounded to 2 decimals.

  CLASS AnalyzerEngine:
    - On init register 'trifecta' -> TrifectaAnalyzer.
    - get_analyzer(name, **overrides):
        if name missing -> raise ValueError.
        instantiate analyzer with overrides for parameters.
```

### Engine Orchestration

```
CLASS OddsEngine(config):
  INIT:
    - Store config.
    - Instantiate adapters list (major active ones: Betfair, BetfairGreyhound, TVG, R&S horse + greyhound,
      AtTheRaces, SportingLife, Timeform, TheRacingApi, Gbgb, Harness).
    - Create httpx.AsyncClient.
    - Connect redis via redis.asyncio.from_url(config.REDIS_URL, decode_responses=True).
    - Log redis initialization.

  close():
    - Close http_client.
    - Close redis_client.

  get_all_adapter_statuses():
    - Return [adapter.get_status() for adapter in adapters].

  _time_adapter_fetch(adapter, date):
    - Record start, await adapter.fetch_races(date, http_client), compute duration.
    - Return tuple (adapter.source_name, result_dict, duration).

  _race_key(race):
    - Lowercase trimmed venue + race_number + formatted start_time (HH:MM).

  _dedupe_races(races):
    - Build map by _race_key.
    - If new key -> store race.
    - Else merge runners (update odds per runner number, append new ones).
    - Return deduped list.

  fetch_all_odds(date, source_filter=None):
    - Compose cache_key "fortuna:races:{date}".
    - If no source_filter -> attempt redis GET, parse via AggregatedResponse.model_validate_json; return on hit.
    - Determine target_adapters (filtered by name if provided).
    - Launch async gather of _time_adapter_fetch for all targets (return_exceptions=True).
    - For each result:
        * If exception -> log error, skip.
        * Extract source_info, override fetch_duration with measured duration.
        * Append to sources list.
        * If status SUCCESS -> extend all_races with result['races'].
    - Dedupe races.
    - Compose response_obj = AggregatedResponse(date parsed, races deduped, sources, metadata containing fetch_time, sources_queried, count success, total_races).
    - If no source_filter -> store in redis with TTL 300 seconds.
    - Return response_obj.model_dump().
```

### API Layer (FastAPI)

```
APP fastapi.FastAPI(title "Checkmate Ultimate Solo API", version "2.1", lifespan context manager):
  lifespan():
    - configure_logging().
    - Load settings via get_settings().
    - Attach OddsEngine(config=settings) to app.state.engine.
    - Attach AnalyzerEngine to app.state.analyzer_engine.
    - On shutdown, engine.close().
  MIDDLEWARE:
    - SlowAPI rate limiting (Limiter key_func get_remote_address, 60/min for adapter status, 30/min for race endpoints).
    - CORSMiddleware with allowed origins from settings.
  DEPENDENCIES:
    - verify_api_key (ensures X-API-Key matches settings.API_KEY except for /health).
    - get_engine to fetch engine from app state.

ROUTES:
  GET /health:
    - Return {"status": "ok", "timestamp": now}.

  GET /api/adapters/status:
    - Rate limited 60/min.
    - Requires API key.
    - Return engine.get_all_adapter_statuses().
    - On error -> HTTP 500.

  GET /api/races/qualified/{analyzer_name} (response_model QualifiedRacesResponse):
    - Rate limited 30/min.
    - Query params: race_date optional (default today), optional overrides for analyzer params.
    - Steps:
        * Determine date_str.
        * aggregated_data = await engine.fetch_all_odds(date_str).
        * Extract races (list of Race models already validated).
        * analyzer_engine = app.state.analyzer_engine.
        * Filter overrides (non-None) into custom_params.
        * analyzer = analyzer_engine.get_analyzer(analyzer_name, **custom_params).
        * result = analyzer.qualify_races(races).
        * Return QualifiedRacesResponse(**result).
    - Handle ValueError -> 404 (missing analyzer).
    - Handle general exception -> 500.

  GET /api/races (response_model AggregatedResponse):
    - Rate limited 30/min.
    - Query: race_date optional, source optional.
    - Determine date, call engine.fetch_all_odds(date_str, source).
    - Return aggregated data (model_dump).
```

### Security

```
MODULE security:
  DEFINE API_KEY_NAME "X-API-Key".
  USE fastapi.security.APIKeyHeader auto_error True.
  verify_api_key(header_value):
    - Fetch settings.
    - Compare to settings.API_KEY via secrets.compare_digest.
    - If match -> return True.
    - Else raise HTTP 403 "Invalid or missing API Key".
```

### Tests

```
tests/test_legacy_scenarios.py:
  PURPOSE: Validate TrifectaAnalyzer behavior through API route.

  HELPER create_mock_runner(number, odds_val, scratched=False):
    - Build Runner with OddsData using decimal odds.

  DEFINE Mock Races (Race models):
    - MOCK_RACE_PASS: 5 runners, odds 3.0, 4.5 etc (passes filters).
    - MOCK_RACE_FAIL_FIELD_SIZE: 11 runners -> exceed field size.
    - MOCK_RACE_FAIL_FAV_ODDS: favorite odds 2.0 (below threshold).
    - MOCK_RACE_FAIL_2ND_FAV_ODDS: second favorite 3.5 (below threshold).

  TEST test_trifecta_analyzer_with_legacy_scenarios:
    - Patch OddsEngine.fetch_all_odds to AsyncMock returning races list.
    - Use FastAPI TestClient (fixture 'client').
    - GET /api/races/qualified/trifecta with headers (X-API-Key).
    - Assert status 200.
    - Expect exactly 1 qualified race (LEGACY_PASS_1) + criteria check.
    - Assert mocked engine fetch awaited once.
```

### Auxiliary Scripts (Backend / Tooling)

```
SCRIPT convert_to_json.py:
  PURPOSE: Convert manifest-listed files into JSON snapshots (sandboxed read).
  STEPS:
    - Configuration: MANIFEST_FILES, OUTPUT_DIR, TIMEOUT.
    - extract_and_normalize_path(line): handle markdown links, backtick paths, bullet lists; convert GitHub raw URLs to local paths.
    - convert_file_to_json_sandboxed(file_path):
        * Launch subprocess to safely read file (avoid sandbox issues).
        * Terminate if exceeds timeout.
    - main():
        * Parse manifests -> gather unique paths.
        * For each path, sandbox read.
        * Save JSON {file_path, content} into OUTPUT_DIR mirroring structure.
        * Report successes/failures; exit 1 if failures.

SCRIPT create_fortuna_json.py:
  PURPOSE: Generate FORTUNA_ALL_PART1/2 JSON bundles.
  PROCESS:
    - Parse manifests -> gather unique paths.
    - For each file:
        * Read content.
        * Categorize: if path starts with "python_service/" or "tests/" -> Part1; else Part2.
    - Write JSON dumps with indentation.
    - Report counts; exit 1 if failures.

SCRIPT chart_scraper.py (ChartScraper class):
  - Manage directories results_archive/{pdf,pdf_unlocked,csv}.
  - Determine yesterday date formats for summary + PDF.
  - _get_yesterday_tracks: fetch Equibase summary page, parse track IDs.
  - _download_and_parse_chart(track_code, chart_date):
      * Build PDF URL pattern.
      * Download PDF (check content-type/length).
      * Save locked/unlocked (via pikepdf).
      * Use tabula.read_pdf to extract tables -> combine -> CSV.
  - run(): orchestrates directories, fetch tracks, iterate, throttle with sleep(1).

SCRIPT command_deck.py (Streamlit):
  - Configure Streamlit page.
  - Load DEV_API_KEY from environment (fallback test key).
  - cached helper get_api_data endpoint -> fetch using requests.
  - UI:
      * Title + description.
      * Sidebar select analyzer (currently only trifecta) and "Clear Cache" button.
      * Display qualified races in DataFrame (normalize nested runners) or info/error messages.
      * Display adapter status DataFrame.

SCRIPT results_parser.py (ChartParser):
  - Provide count_runners(chart_text) scanning "Past Performance Running Line Preview" section; count lines starting with digit until blank or "Trainers:".

SCRIPT live_monitor.py (LiveOddsMonitor class):
  - INIT: store config, instantiate BetfairAdapter.
  - monitor_race(race, http_client):
      * If race ID not from Betfair -> log warning, return race unchanged.
      * Extract market_id.
      * Call adapter.get_live_odds_for_market.
      * Update each runner's odds dict with new OddsData (timestamp now) when selection_id matches.
      * Return updated race.

SCRIPT fortuna_watchman.py (Watchman orchestrator):
  - INIT: load settings, instantiate OddsEngine, AnalyzerEngine, LiveOddsMonitor.
  - get_initial_targets():
      * fetch today's aggregated data.
      * Acquire analyzer (trifecta).
      * Evaluate races -> sorted by score; log top 5.
  - run_tactical_monitoring(targets):
      * With httpx.AsyncClient loop:
          - Determine races within next 5 minutes.
          - For each such race call live_monitor.monitor_race.
          - Remove monitored race from list.
          - Sleep 30 seconds; exit when no active targets.
  - execute_daily_protocol():
      * Log start.
      * Acquire initial targets; if any run monitoring, else log none.
      * Close odds_engine.
      * Log completion.
  - main() entrypoint -> configure logging, instantiate Watchman, run execute_daily_protocol.

WINDOWS Scripts:
  - setup_windows.bat:
      * Verify python installed.
      * Create venv (.venv) if missing.
      * Activate & install python_service/requirements.txt.
      * Verify Node.js; npm install under web_platform/frontend.
      * Print final instructions.

  - run_fortuna.bat:
      * Launch backend uvicorn in new window (activating venv).
      * Launch frontend Next.js in new window.
      * Wait 5 sec, open browser http://localhost:3000.
```

---

## REDIS & CACHING

```
BACKEND relies on redis.asyncio client:
  - namespace "fortuna:races:{date}" for aggregated responses (no source filter).
  - store JSON serialized AggregatedResponse for 5 minutes.
  - On retrieval, validate via Pydantic before returning.

ERROR HANDLING:
  - redis GET/SET exceptions logged but don't halt main flow.
```

---

## DOCUMENTATION (Selected Highlights)

```
ARCHITECTURAL_MANDATE.md:
  - Defines Two-Pillar architecture, Prime Directive.
  - Emphasizes OddsEngine, BaseAdapter, Adapter Fleet, Pydantic models, TrifectaAnalyzer.

HISTORY.md:
  - Chronicles project eras from "Utopian" to "Liberation".
  - Explains environment hostility and shift to portable engine.

ROADMAP_APPENDICES.md:
  - Catalog of adapter backlog categories, intelligence leads, future campaigns (Analyst expansion, legacy tests, dashboard).

WISDOM.md:
  - Provides virtues/vices for agents (operational protocols).
  - Reinforces verifying instructions, small commits, reliance on Project Lead.

README.md:
  - Quick start instructions (setup_windows.bat, run_fortuna.bat).
  - API usage note (API key header requirement).

.env.example:
  - Template for backend credentials + configuration options.
```

---

## FRONTEND PILLAR (web_platform/frontend)

### Configuration & Tooling

```
ENV: Next.js 14 + React 18, Tailwind CSS, TypeScript.

Files:
  - .env.local.example: requires NEXT_PUBLIC_API_KEY + API_URL.
  - next.config.mjs: sets rewrites to proxy /api/* to backend 8000.
  - package.json: dependencies (next, react, socket.io-client), dev dependencies (Tailwind, TypeScript).
  - tailwind.config.ts + postcss.config.js: standard Tailwind setup.
  - tsconfig.json: configure compiler options (strict false, noEmit, Next plugin).
```

### UI Components

```
COMPONENT LiveRaceDashboard (client component):
  STATE:
    races list
    criteria object
    loading boolean
    error string
    lastUpdate timestamp
    params {max_field_size, min_favorite_odds, min_second_favorite_odds}
      - Initialized from localStorage (if available) else defaults.
      - Persist params back to localStorage on change.

  EFFECTS:
    - On mount: fetchQualifiedRaces(initialLoad=True).
    - Set interval every 30s -> fetchQualifiedRaces(False).
    - Cleanup interval on unmount.

  fetchQualifiedRaces(isInitialLoad):
    - Show loading on initial.
    - Reset error.
    - Fetch API key from NEXT_PUBLIC_API_KEY (error if missing).
    - Build query string from params.
    - GET `/api/races/qualified/trifecta` with X-API-Key header.
    - On success: set races, criteria, lastUpdate.
    - On failure: set error message.
    - Toggle loading false when initial load complete.

  handleParamChange:
    - Update params with slider values.

  RENDER:
    - Title, last update timestamp.
    - Control panel with range inputs for parameters (display current values).
    - Conditional messages for loading/error.
    - Summary of number of qualified races.
    - Grid of RaceCard components for each race.

COMPONENT RaceCard:
  PROPS: race (matching Race interface).
  PROCESS:
    - Filter out scratched runners.
    - Sort active runners by number.
    - Count unique odds sources across runners.
    - Determine best odds per runner (min win < 999).
    - formatTimeUntilPost helper -> difference between start_time and now (hours/mins).
    - Render card with:
        * Header (venue, race number, time to post).
        * Qualification score badge (color-coded thresholds).
        * Race condition grid (distance, surface default 'Dirt', field size, sources count).
        * Runner list with stylized badges for top 3 positions (gold/silver/bronze), odds display with source.
```

---

## COMMAND DECK (Streamlit)

```
APPLICATION command_deck.py:
  - Provide alternate dashboard for backend monitoring.
  - Uses st.cache_data for API calls (TTL 30s) with manual clear button.
  - Displays qualified races normalized into DataFrame (runners flattened).
  - Displays adapter statuses DataFrame.
  - Utilizes environment variable DEV_API_KEY or fallback.
```

---

## DATA PROCESSING UTILITIES

```
ChartScraper workflow:
  - Determine yesterday's tracks from Equibase summary HTML.
  - For each track, attempt to download combined PDF (size check).
  - Unlock PDF via pikepdf to remove encryption.
  - Extract tables with tabula (lattice mode).
  - Concatenate to CSV for archival.
  - Delay between requests (1 second) to be polite.

ChartParser (results_parser.py):
  - Parse extracted text to count number of runners by reading the "Past Performance Running Line Preview" section.
```

---

## PROJECT AUTOMATION & DEPLOYMENT

```
setup_windows.bat:
  - Single entry script to prepare backend + frontend dependencies on Windows.

run_fortuna.bat:
  - Launch backend server via uvicorn (auto reload) in new CMD window.
  - Launch Next.js dev server in another window.
  - After delay, open default browser to frontend.

fortuna_watchman.py:
  - Could be scheduled (e.g., cron/Task Scheduler) to run daily.
  - Integrates OddsEngine + Analyzer + LiveOddsMonitor for real-time monitoring.

live_monitor.py:
  - Designed to be invoked close to post time to refresh odds from Betfair.

Redis caching:
  - Requires running redis instance (default local) for performance.
```

---

## END-TO-END FLOW (Narrative Pseudocode)

```
FUNCTION DailyOperation():
  INIT settings = get_settings()
  INIT odds_engine = OddsEngine(settings)
  INIT analyzer_engine = AnalyzerEngine()
  INIT http_client (within odds_engine)
  INIT redis cache.

  FOR each requested API call (/api/races or /api/races/qualified):
    VERIFY API key via security.verify_api_key.
    IF aggregated data cached (and no source filter):
      RETRIEVE from Redis.
    ELSE:
      PARALLEL fetch using adapters:
        - Each adapter fetch_races(date, http_client)
        - Standardize Race/Runner structures.
      MERGE all races with dedupe. (Odds aggregated per runner).
      BUILD AggregatedResponse.
      CACHE (if applicable).
    IF route is /qualified:
      analyzer = analyzer_engine.get_analyzer("trifecta", overrides)
      qualified = analyzer.qualify_races(races)
      RETURN QualifiedRacesResponse.

  FRONTEND LiveRaceDashboard:
    PERIODICALLY fetch /api/races/qualified/trifecta with user-adjusted parameters.
    DISPLAY race cards with scoring, countdown, best odds per runner.

  COMMAND_DECK (Streamlit):
    - Provide alternative interface for developers/operators.

  WATCHMAN automation:
    - At start of day: fetch all races, filter top opportunities.
    - As race times approach: call LiveOddsMonitor to augment with live Betfair odds.
    - Continue until all targets monitored; shutdown.

  CHART PIPELINE (optional offline run):
    - Use ChartScraper to download PDFs and convert to CSV for historical analysis.
    - Use ChartParser to interpret extracted text.

  DOCUMENTATION:
    - Guides architecture decisions, historical context, roadmap, operational wisdom.
```

---

## SUMMARY

```
FortuneFaucet encapsulates:
  - Hardened async backend with resilient adapters, serializer models, caching, analysis engine, HTTP API, security.
  - Multi-source adapter fleet supporting APIs and HTML scrapes, with placeholders for future expansion.
  - Analyzer framework currently featuring Trifecta strategy with scoring.
  - Redis-backed caching and rate-limited FastAPI endpoints.
  - Automated watchman for daily operations and live odds integration.
  - Frontend Next.js dashboard + Streamlit command deck for visualization.
  - Comprehensive documentation capturing mission, history, roadmap, and operational protocols.
  - Tooling scripts for data archiving and Windows-based development workflows.
```

---