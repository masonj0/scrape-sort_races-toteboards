# Project Roadmap: Paddock Parser Next Generation

This document outlines the strategic, phased implementation plan for the project.

## Phase 1: The Foundation - Core Data Acquisition & "Variety"

-   **Goal:** Build a stable, reliable foundation for acquiring and normalizing data from a diverse set of racing disciplines.
-   **Status:** **100% COMPLETE**

### Key Completed Work:
-   **Core Architecture:** Stable `src/` layout, Ruff linter, `pytest` harness, and a resilient, logging-enabled pipeline are in place.
-   **Professional Fetching Engine:** The `ForagerClient` provides robust, human-like fetching with User-Agent rotation and intelligent retries.
-   **Proactive Scraper Defense:** A `Honeypot` utility is in place to detect and avoid scraper traps.
-   **Thoroughbred Adapters:** `EquibaseAdapter`, `SkySportsAdapter`, `RacingPostAdapter`, `AtTheRacesAdapter` are fully operational.
-   **Harness Adapter:** `FanDuelAdapter` provides a high-quality source for Harness racing.
-   **Greyhound Adapter:** `GreyhoundRecorderAdapter` is restored and operational.

---

## Phase 2: The Brain - Advanced Analysis & Data Enrichment

-   **Goal:** Transform the raw data into actionable intelligence.
-   **Status:** **IN PROGRESS**

### Key Completed Work:
-   **Simple Scoring Model:** `RaceScorer` is implemented and tested, based on runner count.
-   **Data Persistence (`Operation Chronicle`):** A `DatabaseManager` using SQLite provides the project with long-term memory and data persistence.

### Immediate Next Steps:
-   **Data Deduplication:** Implement `SmartMerge` logic for combining data from multiple sources and tracking provenance.
-   **Advanced Timezone Handling:** Build a robust system for international race times.
-   **Advanced Scoring Models:** Evolve the `RaceScorer` with more sophisticated, weighted signals beyond the "High Roller" criteria.
-   **Backtesting Engine:** Create a module to validate scoring algorithms against the historical data archive.

---

## Phase 3: The Megaphone - User Interface & Delivery

-   **Goal:** Make the toolkit's insights accessible and actionable.
-   **Status:** **IN PROGRESS**

### Key Completed Work:
-   **Professional CLI:** `run.py` provides a functional `argparse` control panel for core operations.
-   **Web Service API (`Operation Web Weaver`):** A FastAPI-based web service is available at `/api/v1/races` with JSON and CSV export capabilities.
-   **Rich Terminal User Interface (TUI):** An enhanced, `rich`-powered interactive display (`launch_paddock_parser.py`) for running the pipeline and viewing reports in a professional, color-coded table format.
-   **High Roller Report:** An advanced, one-click report in the TUI that automatically filters and sorts races based on user-defined value criteria (imminent start, small field, favorable odds).

### Future Features:
-   **HTML Reports:** Generate clean, user-friendly HTML summaries.
-   **Web Frontend:** Implement a simple web-based dashboard that consumes the FastAPI service.

---

## Phase 4: The Fortress - Security & Resilience

-   **Goal:** Harden the application for robust, long-term, and unattended operation.
-   **Status:** **NOT STARTED**

### Future Features:
-   **The "Persistent Engine":** An "always-on" mode with crash-safe caching.
-   **The `FirewallHandler`:** Intelligent routing and firewall detection beyond the existing Honeypot utility.
