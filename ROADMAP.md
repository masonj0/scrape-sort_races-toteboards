# Paddock Parser V3: Grand Unified Roadmap

This document represents the definitive strategic, architectural, and tactical vision for the Paddock Parser project. It synthesizes our proven V2 accomplishments with the recovered "V3" philosophical pillars and the extensive backlog of our more mature predecessors.

---

## Part 1: The V3 Strategic Pillars (Our Philosophy)

Our future development is guided by four core principles to create a resilient, intelligent, and ethical analytical ecosystem.

*   **On Defense (Mimicking Human Behavior):** Evolve our fetching patterns to introduce sophisticated randomness—"chaos"—to break predictable patterns and more closely mimic the erratic behavior of a real human researcher.

*   **On Architecture (The Intelligent Ecosystem):** Evolve our linear pipeline into a cyclical, learning-based model. This includes a **"Contextualize"** stage (for external data like weather) and a **"Feedback"** loop where real race results are used to continuously improve our scoring models.

*   **On AI Integration (The Hybrid Approach):** Pioneer a hybrid model where LLMs perform **"Dynamic Factor Weighting."** The LLM will analyze qualitative data (pundit commentary, news) to provide a signal that dynamically adjusts the weights in our quantitative scoring engine.

*   **On Ethics (The "Dedicated Human Researcher" Test):** Formally adopt the principle of **"resilient data access."** If a single, dedicated human using browser developer tools could not plausibly achieve our data collection footprint, our methods are too aggressive.

---

## Part 2: The V3 Tactical Roadmap (Our Work)

This section outlines the next generation of features, building upon our stable V2 foundation and guided by the architectural successes of our predecessors.

### Tier 1: Immediate Architectural Evolution
*   **API-First Data Sourcing:** Prioritize the implementation of adapters for API-based sources (e.g., "Racing & Sports," "Sporting Life") over HTML scraping.
*   **Advanced Weighted Scoring:** Evolve the `RaceScorer` into a sophisticated, weighted algorithm, drawing inspiration from the `SCORER_WEIGHTS` in the recovered `config_settings.json`.
*   **Superior Configuration Model:** Refactor our configuration from simple constants to a more flexible, script-based model to manage sources, caching, and HTTP settings.

### Tier 2: Advanced Scraping & Resilience
*   **Playwright Bootstrap Integration:** Implement headless browsers for critical, JavaScript-heavy sites.
*   **Mobile App API Reverse Engineering:** A research task to investigate simpler, less protected mobile APIs for key targets.

---

## Part 3: The V2 "Golden Branch" (Our Foundation)

This section documents the verified, completed features that form the stable foundation for our V3 evolution, categorized by our four architectural pillars.

### The Brain (Scoring & Analysis)
*   **Advanced Weighted Scoring:** A flexible, weighted scoring engine (`scorer.py`) forms the foundation for future analytical models.
*   **Backtesting Engine:** A `Backtester` module for scientifically validating scoring models against historical data.

### The Guardian (Data Integrity & Persistence)
*   **Data Persistence:** A `DatabaseManager` using SQLite provides the project with long-term memory.
*   **Data Deduplication:** `SmartMerge` logic fuses data from multiple sources into a single, authoritative record.

### The Template (Data Acquisition & Resilience)
*   **Professional Fetching Engine:** A resilient `ForagerClient` with User-Agent rotation and intelligent retries.
*   **Initial Adapter Suite:** A functional set of adapters providing our baseline data coverage (`SkySports`, `AtTheRaces`, `RacingAndSports`, etc.).

### The Face (User Experience & Delivery)
*   **Rich Terminal User Interface (TUI):** An enhanced, `rich`-powered interactive display for running reports.
*   **High Roller Report:** A one-click, user-defined value report in the TUI.
*   **Web Service API:** A FastAPI service with JSON and CSV exports.

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
8.  **scrapy-horse-racing:** https://github.com/chrismattmann/scrapy-horse-racing
9.  **horse-racing-data:** https://github.com/jeffkub/horse-racing-data
10. **Greyhound results scraping example:** https://stackoverflow.com/questions/77761268/...
