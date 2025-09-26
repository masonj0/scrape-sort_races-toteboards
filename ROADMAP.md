# ROADMAP V5.0: The Ultimate Engine

This document is the definitive strategic vision for Checkmate V7. It reflects a strategic pivot to a CLI-first approach, prioritizing foundational resilience and data quality over external UIs. Our "Impossible Dream" is to create the most powerful and elegant command-line racing analysis tool in existence.

---

## Part 1: The Prime Directive (The "Checkmate" Endgame)

The sole and exclusive goal of this project is to build and verify a single, specific betting angle. All development is in service of this focused goal.

### The Angle: The "Favorite to Place" Bet
Our purpose is to identify "Checkmate" races and track the historical profitability of a wager that the favorite at post time will finish in either 1st or 2nd place.

### The "Closed Loop" Architecture
To achieve this, we will build a "Closed Loop" system with three core engines: Prediction, Historian, and Accountant.

---

## Part 2: The Tactical Plan (Phased Execution)

### Phase 1: "The Fortress" (Immediate Priority)
*   **Objective:** Achieve production-grade stability and performance for our core infrastructure.
*   **Deliverables:**
    *   **The Water Main:** Implement a singleton pattern with connection pooling for our database connections, making our application more performant and resilient.
    *   **The Dojo:** Harden our test suite by creating `SampleAdapter` and `MockFailureAdapter` for fast, predictable, offline testing of our core orchestration logic.

### Phase 2: "The Ultimate TUI" (The Re-imagined Dream)
*   **Objective:** Evolve our successful "Polished Ticker" CLI into a truly interactive Text User Interface (TUI).
*   **Deliverables:**
    *   **Interactive Mode:** A new `run.py --interactive` mode that allows for sorting, filtering, and deep-diving into race details directly from the terminal.
    *   **Persistent State:** The ability to save and load analysis sessions.

### Phase 3: "The Historian" (Closing the Loop)
*   **Objective:** Build the first half of our "Closed Loop" architecture.
*   **Deliverables:**
    *   **Results Adapters:** A new class of adapters designed to fetch the official results of completed races.
    *   **The Historian Engine:** A service that uses these adapters to populate our database with race outcomes, turning our predictions into auditable history.

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