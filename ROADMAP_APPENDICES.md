# Checkmate: Strategic Appendices

**Purpose:** This document is the permanent home for the high-value strategic intelligence salvaged from the deprecated `ROADMAP.md`. It contains our long-term goals and a library of resources to accelerate development.

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
3.  **Web Scraping for HKJC:** https://gist.github.com/tomfoolc/ef039b229c8e97bd40c5493174bca839
4.  **LibHunt horse-racing projects:** https://www.libhunt.com/topic/horse-racing
5.  **Web data scraping blog:** https://www.3idatascing.com/how-does-web-data-scraping-help-in-horse-racing-and-greyhound/
6.  **Fawazk/Greyhoundscraper:** https://github.com/Fawazk/Greyhoundscraper
7.  **Betfair Hub Models Scraping Tutorial:** https://betfair-datascientists.github.io/tutorials/How_to_Automate_3/
8.  **scrapy-horse-racing:** https://github.com/chrism-attmann/scrapy-horse-racing
9.  **horse-racing-data:** https://github.com/jeffkub/horse-racing-data


## C. Un-Mined Gems (Future Campaign Candidates)

*Discovered during a full operational review. These represent high-value, validated concepts from the project's history that are candidates for future development campaigns.*

### C1. The Intelligence Layer ("The Analyst")

- **Concept:** A dedicated analysis and scoring engine (`analyzer.py`) that sits on top of the `OddsEngine`. It would provide a high-value `/api/races/qualified` endpoint, transforming the API from a data funnel into a source of actionable intelligence.
- **Origin:** Inspired by the `TrifectaAnalyzer` logic in the legacy `checkmate_engine.py` prototype. Formally proposed as "Operation: Activate the Analyst".
- **Value:** Fulfills the project's original vision of finding opportunities, not just collecting data. Creates a clean architectural separation between data collection and business logic.

### C2. The Legacy Test Suite ("The Oracle's Library")

- **Concept:** Repurpose the vast collection of existing tests and mock data located in `attic/legacy_tests_pre_triage`.
- **Origin:** Identified during the full repository file catalog audit.
- **Value:** Provides a massive shortcut to production hardening. Allows the project to increase test coverage and resilience by validating the CORE services against hundreds of historical edge cases.

### C3. The AI Architectural Reviews ("The Council's Wisdom")

- **Concept:** Synthesize the expert analysis and architectural recommendations from the multiple AI model reviews stored in the Digital Attic (`*.md.txt` files).
- **Origin:** Explicitly mentioned in the Gemini928 handoff memo as "Architectural Parables".
- **Value:** A source of high-level architectural consulting. These documents may contain actionable advice on performance, security, or design patterns that could significantly improve the current architecture.

### C4. The Interactive Dashboard Prototype ("The Command Deck")

- **Concept:** Create a modern, internal, real-time command deck for visualizing engine data and testing new `Analyzer` models.
- **Origin:** Inspired by the `portable_demo_v2.py` Streamlit application from the attic.
- **Value:** An invaluable tool for development, debugging, and real-time operational insight, far more intuitive than raw logs or API calls.