# ROADMAP V4.0: The Checkmate Endgame

This document is the definitive strategic and tactical vision for the Checkmate V7 project. It fuses our high-level strategic purpose with a clear, phased execution plan.

---

## Part 1: The Prime Directive (The "Checkmate" Endgame)

The sole and exclusive goal of this project is to build and verify a single, specific betting angle. All development is in service of this focused goal.

### The Angle: The "Favorite to Place" Bet
Our purpose is to identify "Checkmate" races that meet our dynamic, odds-based criteria, and then to track the historical profitability of a single bet within those races: a wager that the favorite at post time will finish in either 1st or 2nd place.

### The "Closed Loop" Architecture
To achieve this, we will build a "Closed Loop" system with three core engines:
1.  **The Prediction Engine:** Our live monitor (the current `checkmate_v7` application) that finds and logs pre-race opportunities.
2.  **The Historian Engine:** A new class of adapters that fetches official race results and payout values.
3.  **The Accountant Engine:** An analytical process that joins predictions with results to calculate the long-term ROI of our strategy.

---

## Part 2: The Tactical Plan (Phased Execution)

### Phase 1: "The Grand Fleet" (Immediate Priority)
*   **Objective:** Achieve data dominance by integrating our backlog of proven, high-value adapters.
*   **Deliverables:**
    *   Refactor and integrate the `TVGAdapter`.
    *   Refactor and integrate the `BetfairExchangeAdapter`.
    *   Refactor and integrate the `OddsAPIAdapter`.

### Phase 2: "The Cockpit & The Crier" (The User Experience)
*   **Objective:** Build the first tangible, user-facing manifestations of our "Impossible Dream."
*   **Deliverables:**
    *   **The Cockpit:** A V1 React-based dashboard.
    *   **The Crier:** A V1 `SlackAlerter`.

### Phase 3: "The Dojo" (The Quality Gate)
*   **Objective:** Harden our test suite and accelerate development.
*   **Deliverables:**
    *   Create and integrate `SampleAdapter` and `MockFailureAdapter` for testing.

---

## Appendix A: V3 Adapter Backlog (The "Treasure Chest")

This is the definitive, prioritized list of data sources to be implemented.

### Category 1: High-Value Data Feeds (API-First)
*   BetfairDataScientistThoroughbred
*   BetfairDataScientistGreyhound
*   racingandsports
*   sportinglife
*   racingpost

### Category 2-6: Global Sources, North American, European, etc.
*   (Full categorized list from the source document to be included here)

---

## Appendix B: Open-Source Intelligence Leads

A curated list of projects and resources to accelerate development.

1.  **joenano/rpscrape:** https://github.com/joenano/rpscrape
2.  **Daniel57910/horse-scraper:** https://github.com/Daniel57910/horse-scraper
3.  **Web Scraping for HKJC:** https://gist.github.com/tomfoolc/ef039b229c8e97bd40c5493174bca839
4.  (Full list of 10 leads to be included here)