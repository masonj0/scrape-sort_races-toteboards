# Fortuna Faucet: Strategic Roadmap & Un-Mined Gems

This document contains the high-level strategic roadmap and a curated list of architectural blueprints and open-source intelligence for future development.

---

## 💎 Primo Code: The Ascended Kingdom Blueprint

This grid, synthesized from a comprehensive Claude audit, represents the primary strategic roadmap for elevating Fortuna Faucet into a professional-grade, enterprise-ready application.

| Category | Feature | Description & Strategic Value |
| :--- | :--- | :--- |
| **Production Hardening** | **Comprehensive Error Handling** | A full-fledged `ErrorRecoveryMiddleware` with a stateful, per-adapter **Circuit Breaker** to prevent cascading failures and improve system resilience. |
| **Production Hardening** | **Health Monitoring Dashboard** | A `/health/detailed` API endpoint that provides deep system metrics, including CPU/memory usage and historical health data for each adapter. |
| **Advanced Analytics** | **Historical Performance Tracker** | A `PerformanceTracker` class to record actual race *results* and compare them against our *predictions*, enabling measurement and improvement of the analyzer's accuracy. |
| **Advanced Analytics** | **Pattern Recognition Engine** | A `PatternDetector` to find profitable patterns across venues, times, and odds, turning historical data into actionable intelligence. |
| **User Experience** | **Desktop Notifications System** | A frontend-based `DesktopNotificationManager` to provide native, clickable Windows notifications for high-value races. |
| **User Experience** | **Advanced Race Filtering** | A new, expandable `AdvancedFilters.tsx` component for the UI to allow for much more granular race selection. |
| **User Experience** | **Export & Reporting Features** | An `ExportManager.ts` for the frontend to export data to professionally formatted, multi-sheet **Excel** files or simple **CSV** files. |
| **Tooling** | **Professional Installer** | A script to generate a polished, professional Windows installer using **Inno Setup** to create a single, distributable `.exe`. |
| **Tooling** | **Portable Deployment Package** | A `create_portable.bat` script to bundle the entire application into a self-contained, portable zip file. |

---

## 🏛️ Future Architectural Campaigns

These are high-value, strategic objectives preserved from earlier planning phases.

### Campaign: The Ascended Analyzer

**The Vision:** The current TrifectaAnalyzer is powerful but monolithic. The next evolution is to refactor it into a more configurable and extensible engine.

**Key Objectives:**
*   **Configurable Weights:** Allow the weights for `field_size_score` and `odds_score` to be configured via environment variables or a settings file.
*   **Strategy Plugins:** Design a system where new "Analyzers" can be dropped in as plugins without modifying the core engine. This would allow for the easy addition of new strategies (e.g., `ExactaAnalyzer`, `LongshotAnalyzer`).
*   **Dynamic Loading:** The API should be able to dynamically discover and load any available analyzer plugins.

### Campaign: The Legacy Test Harness

**The Vision:** The project's `attic` contains a wealth of historical test cases and scenarios. These represent invaluable ground-truth data. This campaign is focused on resurrecting this data into a modern `pytest` test harness.

**Key Objectives:**
*   **Data Migration:** Convert the old test data (if in custom formats) into modern fixtures (e.g., JSON, YAML).
*   **Test Modernization:** Rewrite the core logic of the legacy tests using modern `pytest` conventions, `asyncio` support, and proper mocking.
*   **CI Integration:** Ensure the new test harness is fully integrated into our continuous integration pipeline.

---

## 📚 Open Source Intelligence & Technology Watchlist

A curated list of noteworthy technologies and projects for future consideration.

*   **PDF Parsing Technology:** The `pdfplumber` library has been identified as a potentially superior alternative to our current PDF parsing methods. It should be the primary candidate for any future refactoring of the `ResultsParser`.
*   **`kenthunt/chart-parser`:** [https://github.com/kenthunt/chart-parser](https://github.com/kenthunt/chart-parser) - A highly relevant, offline PDF chart parser that serves as an excellent architectural reference.
*   **`ccmd00d/handycapper`:** [https://github.com/ccmd00d/handycapper](https://github.com/ccmd00d/handycapper) - Another open-source project in the same domain, valuable for comparative analysis and identifying alternative data sources or techniques.

---

## Appendix A: The Grand Adapter Backlog

*(This section is preserved for historical and strategic continuity. It represents the original, ambitious vision for the adapter fleet.)*

This is a prioritized list of data adapters that are either stubs or have not yet been implemented. The goal is to achieve the most comprehensive data coverage possible.

### Tier 1: Critical (US Racing Coverage)

*   **BrisnetAdapter:** Essential for past performance (PP) data, workout information, and proprietary ratings.
*   **DRFAdapter (Daily Racing Form):** The gold standard for race entries, results, and news. A critical component for a complete US racing picture.
*   **EquibaseAdapter (Full Implementation):** While we have a chart scraper, a full adapter for entries and other data points is needed.
*   **XpressbetAdapter:** Access to another major tote provider's data.

### Tier 2: High Priority (Major International & US Betting)

*   **FanDuelAdapter / DraftKingsAdapter:** Access to major sportsbook odds, especially for fixed-odds racing.
*   **NYRABetsAdapter:** Critical for deep coverage of New York's premier tracks (Saratoga, Belmont, Aqueduct).
*   **HorseRacingNationAdapter:** Excellent source for workout data, news, and community sentiment.

### Tier 3: Medium Priority (International Expansion)

*   **RacingPostAdapter (UK/IRE):** The UK's equivalent of the Daily Racing Form. Essential for expanding into European racing.
*   **PuntersAdapter (AUS):** A key source for Australian racing data.
*   **TabAdapter (AUS):** The primary tote provider in Australia.
*   **RacingTVAdapter (UK):** Another major source for UK racing information and live feeds.

### Tier 4: Exploratory & Niche

*   **PointsBetAdapter:** Another sportsbook with unique odds and promotions.
*   **CalRacingAdapter:** Specific data for California tracks.
*   **OffTrackBettingAdapter (OTB):** Potential source for smaller track data.
