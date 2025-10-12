## Pseudocode Overview of the Fortuna Faucet Product Package

### 0. Artifact Inventory
- DEFINE `PART1` := Core Python backend modules.
- DEFINE `PART2` := Adapter fleet + integration components.
- DEFINE `PART3` := Frontend, Windows toolchain, documentation, operational utilities.

---

### 1. Installation & Bootstrap Workflow
```
SYSTEM_BOOTSTRAP():
    WHEN user executes INSTALL_FORTUNA.bat AS administrator:
        VERIFY Python 3.11 installed; INSTALL if missing.
        VERIFY Node.js LTS installed; INSTALL if missing.
        CREATE Python virtual environment (.venv).
        INSTALL backend dependencies via requirements.txt.
        NAVIGATE to web_platform/frontend; npm install.
        RUN CREATE_SHORTCUTS.bat to place desktop launchers.
        REPORT success; await user confirmation.

    WHEN user runs LAUNCH_FORTUNA.bat:
        IF .env missing THEN warn user and abort.
        // This script now delegates to the superior PowerShell launcher.
        CALL launcher.ps1 with execution policy bypass, which:
            STARTS FastAPI backend via uvicorn in minimized console.
            WAITS a few seconds for API startup.
            STARTS Next.js frontend development server.
            DELAYS to ensure readiness.
            STARTS fortuna_monitor.py for live status dashboard.
            OPENS default browser to http://localhost:3000.
        DISPLAY "All Systems Operational"; wait for user input.

    WHEN user triggers STOP_FORTUNA.bat:
        TERMINATE backend, monitor, and frontend console windows by title filter.
        CONFIRM shutdown to user.

    WHEN user runs RESTART_FORTUNA.bat:
        APPEND timestamp to restart log.
        CALL stop script, delay, then call launch script.
        LOG completion.

    WHEN user runs SCHEDULE_FORTUNA.bat AS admin:
        REGISTER on-logon task launching PowerShell launcher.
        REGISTER daily restart task at 03:00 via RESTART_FORTUNA.bat.
        INFORM user automated scheduling active.

    WHEN user runs setup_windows.bat:
        PERFORM minimal verification + dependency installs without admin tasks.
        COPY .env.local example for frontend if missing.
```

---

### 2. Configuration & Documentation Layer
```
CONFIGURE_ENVIRONMENT():
    COPY .env.example -> .env; populate API_KEY and third-party credentials.
    SET optional adapters (Betfair, TVG, Racing & Sports, PointsBet) credentials.
    DEFINE ALLOWED_ORIGINS for CORS.
    CONFIGURE Redis cache URL if non-default.
    SPECIFY GREYHOUND_API_URL and THE_RACING_API_KEY when available.

DOCUMENTATION_PORTAL():
    READ README.md for quick start instructions.
    CONSULT README_WINDOWS.md for desktop experience.
    STUDY ARCHITECTURAL_MANDATE.md for two-pillar system doctrine.
    REVIEW ROADMAP_APPENDICES.md for strategic backlog and intelligence.
    ABSORB HISTORY.md for project chronology.
    INTERNALIZE WISDOM.md for operational virtues & vices.
```

---

### 3. Backend Pillar (FastAPI + Async Engine)
```
BACKEND_SERVICE_STARTUP():
    ON uvicorn launch of python_service.api:app:
        LOAD settings via python_service.config.get_settings.
        INSTANTIATE FortunaEngine (OddsEngine) with async orchestration.
        REGISTER REST endpoints (e.g., /api/races/qualified/<analyzer>, /api/adapters/status, /health).
        ENFORCE X-API-Key header based on .env API_KEY except for /health.
        RESPOND with validated Pydantic models.

ODDS_ENGINE_PIPELINE():
    WHEN client requests daily races:
        GATHER asynchronous tasks across adapter fleet.
        NORMALIZE data into python_service.models.Race structures.
        RETURN aggregated payload with metadata and instrumentation.

ADAPTER_FLEET (PART2):
    FOR each adapter in python_service/adapters:
        IMPLEMENT BaseAdapter interface with resilient error handling.
        AUTHENTICATE using adapter-specific credentials.
        FETCH odds, runners, and metadata from source.
        TRANSFORM raw payloads into standardized Runner & OddsData models.
        RECORD status, duration, success flag.

ANALYSIS_LAYER():
    INSTANTIATE AnalyzerEngine.
    WHEN endpoint /api/races/qualified/<strategy> invoked:
        RETRIEVE analyzer (e.g., TrifectaAnalyzer).
        EVALUATE races on scoring rules.
        RETURN filtered + ranked Race list with qualification_score.
```

---

### 4. Strategic Orchestration & Monitoring
```
FORTUNA_WATCHMAN():
    CONFIGURE structlog via python_service.logging_config.
    CALL get_initial_targets():
        REQUEST today's races via OddsEngine.
        APPLY AnalyzerEngine.trifecta to score and sort.
        LOG top opportunities.
    CALL run_tactical_monitoring(targets):
        ENTER async context LiveOddsMonitor with BetfairAdapter.
        LOOP until targets empty:
            IDENTIFY races within 5-minute window.
            FOR each imminent race:
                FETCH live odds via Betfair API.
                UPDATE race runner odds.
                REMOVE race from monitoring queue.
            SLEEP 30 seconds between checks.
    AFTER completion:
        CLOSE OddsEngine resources.
        LOG mission completion.

LIVE_ODDS_MONITOR():
    WHEN monitoring Betfair market:
        VALIDATE race ID originates from Betfair.
        REQUEST real-time odds via betfair_adapter.get_live_odds_for_market.
        IF odds received:
            UPDATE runner.odds[source] with new OddsData (win price, timestamp).
        HANDLE exceptions gracefully; log warnings.

FORTUNA_MONITOR (Tkinter GUI):
    ON launch:
        LOAD API_KEY from .env.
        INITIALIZE themed dashboard with stat cards + tree table.
        OPTIONALLY ENABLE performance graphs via matplotlib.
        SET auto-refresh interval (30 seconds default).
    ON refresh:
        REQUEST /api/adapters/status with API key.
        UPDATE UI with adapter metrics, success rate, durations.
        APPEND data to PerformanceTracker history.
        RENDER graphs if available.
        PROVIDE manual refresh and quick link to frontend dashboard.
```

---

### 5. Data Acquisition & Processing Utilities
```
CHART_SCRAPER():
    DETERMINE yesterday's date in summary + PDF formats.
    FETCH track summary HTML from equibase static summary.
    PARSE track codes via BeautifulSoup.
    FOR each track:
        CONSTRUCT combined daily PDF URL.
        DOWNLOAD with size/content-type validation.
        SAVE locked PDF to results_archive/pdf.
        UNLOCK via pikepdf into pdf_unlocked.
        EXTRACT tables via tabula.read_pdf (lattice mode).
        CONCAT DataFrames into CSV stored in results_archive/csv.
        PAUSE briefly between tracks to respect rate limits.

RESULTS_PARSER.ChartParser:
    FUNCTION count_runners(chart_text):
        LOCATE "Past Performance Running Line Preview" block.
        ITERATE rows; count lines starting with numeric program number.
        RETURN total runner count.

COMMAND_DECK (Streamlit):
    CONFIGURE Streamlit layout wide.
    LOAD DEV_API_KEY from .env.
    DEFINE cached helper get_api_data(endpoint).
    DISPLAY qualified races table (flattening runner data).
    DISPLAY adapter status DataFrame.
    PROVIDE analyzer selection and cache clear button.

FORTUNA_WATCHMAN + LIVE MONITOR synergy ensures end-to-end automation of handicapping cycle.
```

---

### 6. Review & Packaging Scripts
```
CONVERT_TO_JSON():
    READ MANIFEST2.md, MANIFEST3.md.
    EXTRACT file paths via enlightened parsing (links, backticks, bullet formats).
    FOR each file:
        SPAWN sandboxed process to read contents with timeout.
        WRITE JSON backups under ReviewableJSON/<path>.json.
    EXIT with failure code if any file processing fails.

CREATE_FORTUNA_JSON():
    READ MANIFEST, MANIFEST2, MANIFEST3.
    NORMALIZE paths (handling URLs, formatting).
    CATEGORIZE:
        IF path starts with python_service/adapters → PART2 (Adapter Fleet).
        ELSE IF path starts with python_service/ → PART1 (Core Backend).
        ELSE → PART3 (Frontend, docs, tooling).
    WRITE three JSON packages:
        FORTUNA_ALL_PART1.JSON, FORTUNA_ALL_PART2.JSON, FORTUNA_ALL_PART3.JSON.
    REPORT statistics; exit non-zero if failures occurred.
```

---

### 7. Frontend Pillar (Next.js + TypeScript)
```
FRONTEND_BOOT():
    REQUIRE .env.local with NEXT_PUBLIC_API_KEY + API_URL.
    Next.js 14.1 + React 18 environment with Tailwind, React Query, socket.io-client.
    PWA support via next-pwa (disabled in development).

APP_STRUCTURE:
    Providers.tsx:
        INITIALIZE TanStack QueryClient.
        WRAP children with QueryClientProvider.

    LiveRaceDashboard.tsx:
        DEFINE local filter state (minScore, maxFieldSize, sortBy).
        useQuery 'qualifiedRaces':
            CALL fetchQualifiedRaces (proxy to backend via API route).
        useQuery 'adapterStatuses':
            CALL fetchAdapterStatuses (fetch /api/adapters/status).
        PROCESS races:
            FILTER by score and field size.
            SORT based on selected criterion.
        RENDER:
            Header + adapter status pills.
            Filter controls (range sliders, selects).
            Race grid using RaceCard components.
            Error/loading messaging.

    RaceCard.tsx:
        RECEIVE Race.
        FILTER out scratched runners.
        SORT remaining by program number.
        CALCULATE best odds per runner across sources.
        DISPLAY:
            Venue, race number, time to post.
            Qualification score badge with color tiers.
            Conditions grid (distance, surface, field size, source count).
            Runner rows with jockey/trainer info and best odds.

STYLING_LAYER:
    Tailwind config scanning app/, pages/, components/.
    Dark-mode friendly UI with gradients and hover transitions.

BUILD_SCRIPTING:
    npm run dev → Next.js dev server.
    npm run build/start for production pipeline.
```

---

### 8. Windows Desktop Experience
```
DESKTOP_SHORTCUTS():
    CREATE "Launch Fortuna" pointing to LAUNCH_FORTUNA.bat.
    CREATE "Fortuna Monitor" executing fortuna_monitor.py via venv Python.
    CREATE "Stop Fortuna" linking to STOP_FORTUNA.bat.
    ASSIGN shell32 icons and descriptions.

TASK_SCHEDULER_INTEGRATION():
    launcher.ps1 (referenced) manages orchestrated startup (not included in snippet).
    Daily restart ensures resilience against long-running drift.
```

---

### 9. Governance & Philosophy
```
ARCHITECTURAL_MANDATE:
    ENFORCE two-pillar doctrine: asynchronous Python backend + TypeScript frontend.
    EMPHASIZE OddsEngine, BaseAdapter resilience, Pydantic contracts, TrifectaAnalyzer.

HISTORY + WISDOM:
    PRESERVE project chronicles from Utopian Era to Liberation.
    APPLY Eight Virtues (authority, verification, precision, TDD, communication, adherence, self-reliance, humility).
    AVOID Eight Vices (assumption, improvisation, blind trust, negligence, impurity, independence, hubris, impatience).

ROADMAP_APPENDICES:
    MAINTAIN adapter backlog priorities.
    CURATE open-source intelligence references.
    TRACK future campaign candidates (Analyzer, Legacy tests, AI reviews, Command Deck).
```

---

### 10. Overall Control Flow Summary
```
DAILY_OPERATION():
    USER ensures API keys configured.
    SCHEDULED startup (or manual LAUNCH):
        START backend API (FastAPI + uvicorn).
        START frontend dashboard (Next.js).
        OPEN Fortuna Monitor (Tkinter) for operational oversight.
    BACKEND executes adapters → OddsEngine → Analyzer.
    FRONTEND pulls qualified races + adapter status for user visualization.
    WATCHMAN (optional) automates target acquisition + live monitoring.
    DATA UTILITIES (chart_scraper, results_parser) enrich historical datasets.
    MONITOR logs + dashboards ensure system health.
    DAILY restart maintains stability; STOP script performs clean shutdown.
    DOCUMENTATION guides ongoing development aligned with project virtues.
```