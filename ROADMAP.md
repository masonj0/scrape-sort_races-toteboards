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
*   **Enlightened Scorer:** A dynamic, multi-factor scoring engine (`RaceScorer` in `scorer.py`). It uses a "Trifecta of Factors" (field size, favorite's odds, and contention) and a user-configurable weighting system in `config.py` to produce a transparent, detailed score for each race.
*   **Backtesting Engine:** A `Backtester` module for scientifically validating scoring models against historical data.

### The Guardian (Data Integrity & Persistence)
*   **Data Persistence:** A `DatabaseManager` using SQLite provides the project with long-term memory.
*   **Data Deduplication:** `SmartMerge` logic fuses data from multiple sources into a single, authoritative record.

### The Template (Data Acquisition & Resilience)
*   **Dual-Track Data Acquisition:** A new, two-pronged strategy for data collection.
    *   **API-First (The Diplomat):** Prioritizes clean, structured data from GraphQL and other web APIs (e.g., FanDuel).
    *   **Resilient Scraping (The Soldier):** A robust `fetcher.py` module with `tenacity`-based retries, exponential backoff, and User-Agent rotation for gracefully handling traditional HTML scraping.
*   **Expanded Adapter Fleet:** A vast suite of resurrected and V3-modernized adapters, including premier API-driven sources (**Racing Post, FanDuel**) and comprehensive HTML scrapers (**Timeform, Equibase**), providing extensive data coverage.

### The Face (User Experience & Delivery)
*   **Rich Terminal User Interface (TUI):** An enhanced, `rich`-powered interactive display for running reports.
*   **High Roller Report:** A one-click, user-defined value report in the TUI.
*   **Web Service API:** A FastAPI service with JSON and CSV exports.

---

## Appendix A: V3 Adapter Backlog (The "Treasure Chest")

This is the definitive, prioritized list of data sources to be implemented.

---

## Part 4: The "Checkmate" Endgame (September 2025)

After achieving a stable V4 architecture and a powerful, multi-source data pipeline, the project has received its final, unifying Prime Directive from its solitary, final customer. The sole and exclusive goal of the "Modern Renaissance" is now to build and verify a single, specific betting angle.

### The Prime Directive: The "Favorite to Place" Angle

The application's purpose is to identify "Checkmate" races that meet a dynamic, odds-based criteria, and then to track the historical profitability of a single, specific bet within those races: the **"Favorite to Place"** bet (a wager that the favorite at post time will finish in either 1st or 2nd place).

All future development will be in service of this single, laser-focused goal.

### The "Closed Loop" Architecture

To achieve this, the project will be evolved into a "Closed Loop" analytical system with three core engines:

1.  **The Prediction Engine:** A live monitor that uses our V3 adapters to find pre-race "Checkmate" opportunities and logs them to a permanent database.

2.  **The Historian Engine:** A new class of results-focused adapters designed for one purpose: to fetch the official results of a completed race and, crucially, to extract the specific **payout value** for the favorite's "Place" finish.

3.  **The Accountant Engine:** A final, analytical process that joins the predictions with the results to calculate the precise, long-term **Return on Investment (ROI)** of the "Favorite to Place" strategy. The final output will be a cumulative P/L graph, which will serve as the project's ultimate report card.

---

## Part 5: The New Reality: The Hybrid System

The project's architecture has been formalized into two distinct but connected systems:

*   **The Engine (Python Backend):** A powerful, headless API server responsible for all data acquisition, analysis, and persistence. Its features are documented under the V2 "Golden Branch" section.
*   **The Cockpit (React Frontend):** A production-grade React application that serves as the project's primary user interface. It is the definitive "Face" of the system.

---

## Part 6: The "Symbiosis" Endgame (September 2025)

The "Checkmate" Endgame has evolved. The new Prime Directive is to achieve a perfect, seamless integration between our powerful Python Engine and our beautiful React Cockpit.

### The New Prime Directive: "Operation: Symbiosis"

The application's purpose is to connect the live, analytical data from the Python backend to the React frontend, creating a single, cohesive, and powerful user experience. All future development will be in service of this integration.

### The "Closed Loop" Architecture

The three engines (Prediction, Historian, Accountant) will be implemented within the Python backend. The React frontend will provide the interface for visualizing the data from these engines, including the cumulative P/L graph which remains the project's ultimate report card.
