# ROADMAP V6.0: The Live Cockpit

This document is the definitive strategic vision for Checkmate V7. It reflects a strategic breakthrough based on a new, achievable architectural blueprint for a real-time web application. This new roadmap obsoletes all previous versions.

Our "Impossible Dream" is no longer a CLI tool; it is the creation of the live, interactive, and professional-grade web application defined in the `checkmate_web_app_pseudocode.md` artifact. This is the new North Star.

---

## Part 1: The Prime Directive

The sole and exclusive goal of this project is to build and verify a single, specific betting angle. All development is in service of this focused goal.

### The Angle: The "Favorite to Place" Bet
Our purpose is to identify "Checkmate" races and track the historical profitability of a wager that the favorite at post time will finish in either 1st or 2nd place.

### The "Closed Loop" Architecture
To achieve this, we will build a "Closed Loop" system with three core engines: Prediction, Historian, and Accountant. The new web application will serve as the primary interface for this entire system.

---

## Part 2: The Tactical Plan (The Web App Campaign)

This plan is a direct, phased implementation of the `checkmate_web_app_pseudocode.md` blueprint.

### Phase 1: "The Engine Room" (Backend Foundation)
*   **Objective:** To stand up the core FastAPI server and port our perfected portable engine logic into a modular, web-ready format.
*   **Deliverables:**
    1.  Create the new `checkmate_web/` project directory.
    2.  Implement `main.py` with a basic FastAPI app.
    3.  Implement a static file server to serve the (initially empty) `index.html`, `app.js`, and `style.css` files.
    4.  Create `engine.py` and migrate the complete, battle-tested `DataSourceOrchestrator` and `TrifectaAnalyzer` classes from our `checkmate_engine.py` artifact into it.
    5.  Establish the in-memory `CACHE` dictionary in `main.py` for global state management.

### Phase 2: "The API Surface" (Data Endpoints)
*   **Objective:** To build and verify the complete set of read-only API endpoints that will power the frontend.
*   **Deliverables:**
    1.  Implement the `/api/status` endpoint.
    2.  Implement the `/api/adapters/status` endpoint.
    3.  Implement the `/api/races/all` endpoint.
    4.  Implement the `/api/races/qualified` endpoint.
    5.  Implement the `startup_event` to perform an initial data fetch when the server starts.

### Phase 3: "The Cockpit V1" (Visual Interface)
*   **Objective:** To build the complete, non-interactive visual front-end of the application.
*   **Deliverables:**
    1.  Implement the full HTML structure in `static/index.html` as defined in the pseudocode.
    2.  Implement the full, modern CSS in `static/style.css` to create the polished, professional look.
    3.  In `static/app.js`, implement the JavaScript logic to:
        *   Fetch data from all API endpoints on page load.
        *   Dynamically render the Adapter Status grid.
        *   Dynamically render the Race Cards for both the "Qualified" and "All Races" tabs.
        *   Implement the tab-switching logic.

### Phase 4: "The Live Engine" (Interactivity & Control)
*   **Objective:** To make the application fully interactive and live.
*   **Deliverables:**
    1.  Implement the `POST /api/refresh` endpoint with background tasks in `main.py`.
    2.  Implement the `GET` and `POST` endpoints for `/api/settings`.
    3.  In `static/app.js`, implement the JavaScript logic for:
        *   The "Refresh Data" button, including the polling mechanism to wait for completion.
        *   The Settings Modal (opening, closing, populating with data).
        *   The "Save Settings" functionality, which sends the updated configuration to the backend.
        *   The auto-refresh timer to periodically update the system status.

---

## Appendix A: V3 Adapter Backlog (The "Treasure Chest")

This is the definitive, prioritized list of data sources to be implemented.

### Category 1: High-Value Data Feeds (API-First)
*   BetfairDataScientistThoroughbred
*   BetfairDataScientistGreyhound
*   racingandsports
*   sportinglife (requires investigation)
*   racingpost (requires auth)

### Category 2: Premium Global Sources (Scraping)
*   timeform
*   attheraces
*   racingtv
*   oddschecker
*   betfair
*   horseracingnation
*   brisnet

### Category 3: North American Authorities & ADWs
*   equibase
*   drf
*   fanduel
*   twinspires
*   1stbet
*   nyrabets
*   xpressbet

### Category 4: European Authorities & Markets
*   francegalop
*   deutschergalopp
*   svenskgalopp
*   pmu

### Category 5: Asia-Pacific & Rest of World
*   tab
*   punters
*   racingaustralia
*   hkjc
*   jra
*   goldcircle
*   emiratesracing

### Category 6: Specialized Disciplines (Harness & Greyhound)
*   usta
*   standardbredcanada
*   harnessracingaustralia
*   gbgb
*   grireland
*   thedogs

---

## Appendix B: Open-Source Intelligence Leads

A curated list of projects and resources to accelerate development.

1.  **joenano/rpscrape:** https://github.com/joenano/rpscrape
2.  **Daniel57910/horse-scraper:** https://github.com/Daniel57910/horse-scraper
3.  **Web Scraping for HKJC:** https://gist.github.com/tomfoolc/ef039b229c8e97bd40c5493174bca839
4.  **LibHunt horse-racing projects:** https://www.libhunt.com/topic/horse-racing
5.  **Web data scraping blog:** https://www.3idatascing.com/how-does-web-data-scraping-help-in-horse-racing-and-greyhound/
6.  **Fawazk/Greyhoundscraper:** https://github.com/Fawazk/Greyhoundscraper
7.  **Betfair Hub Models Scraping Tutorial:** https://betfair-datascientists.github.io/tutorials/How_to_Automate_3/
8.  **scrapy-horse-racing:** https://github.com/chrism-attmann/scrapy-horse-racing
9.  **horse-racing-data:** https://github.com/jeffkub/horse-racing-data
10. **Greyhound results scraping example:** https://stackoverflow.com/questions/77761268/...