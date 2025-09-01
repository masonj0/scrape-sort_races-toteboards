# Paddock Parser NG: Development Roadmap

This document outlines the strategic vision and multi-phase implementation plan for the Paddock Parser NG project. Our goal is to evolve this toolkit into a professional-grade, resilient, and intelligent data analysis engine.

---

## 1. Strategic Pillars

Our development is guided by four core principles that define our architecture and operational philosophy.

*   **On Resilience: The "Professional Fetching Engine"**
    *   **Core Insight:** Our greatest vulnerability is appearing as a predictable, automated scraper.
    *   **Strategic Response:** We will build a "Professional Fetching Engine" that mimics human behavior and is resilient to network interference. This includes User-Agent rotation, random delays, intelligent retries with exponential backoff, proxy support, and the ability to detect and bypass corporate firewalls by using alternative URLs.

*   **On Intelligence: The "Smart Merge" & Analysis Engine**
    *   **Core Insight:** The true value of our application comes from intelligently synthesizing data from multiple sources into a single, unified view.
    *   **Strategic Response:** We will implement a "Smart Merge" engine for data deduplication and provenance tracking. This allows us to combine partial data from different adapters into a complete and accurate picture. Our analysis engine will focus on a configurable "value score" to rank opportunities.

*   **On Architecture: The "Persistent Engine" & API-First Design**
    *   **Core Insight:** The application must be able to operate in both a batch-processing mode and an "always-on" persistent mode for continuous monitoring.
    *   **Strategic Response:** We will build a "Persistent Engine" that can run continuously, manage a crash-safe cache, and provide real-time analysis. Our architecture will be "API-First", with a primary focus on GraphQL-powered sources.

*   **On Ethics: The "Dedicated Human Researcher" Test**
    *   **Core Insight:** If a single, dedicated human using browser developer tools could not plausibly achieve the same data collection footprint, our methods are too aggressive.
    *   **Strategic Response:** We will formally adopt this principle, reframing our approach as **"resilient data access"** for a sustainable and ethical long-term strategy. We will always respect `robots.txt` and website terms of service.

---

## 2. Implementation Roadmap

### Phase 1: The Foundation (Complete)
This phase focused on unifying the project structure, stabilizing the core components, and building a flexible command-line interface.

-   **Project Unification:** Migrated to a standard `src` layout.
-   **Core Adapters:** Restored and tested the `SkySportsAdapter` and `FanDuelAdapter`.
-   **Professional CLI:** Implemented a powerful CLI using `argparse`, allowing for configurable pipeline execution.
-   **Async Pipeline:** Refactored the core pipeline to be asynchronous, supporting both sync and async adapters.
-   **Architectural Restoration:** Completed "Operation Sanctuary" to restore the Golden Branch from a critical corruption event, solidifying the project's foundation.

### Phase 2: The Brain (Professional Fetching Engine)
This phase focuses on making our data gathering dramatically more resilient and intelligent.

Key Future Features:
-   **User-Agent & Fingerprint Rotation:** Implement rotation of User-Agents and other browser fingerprints to avoid blocking.
-   **Intelligent Retries & Backoff:** Implement a resilient `get` method with exponential backoff for 429/5xx errors.
-   **Advanced Caching:** Implement a crash-safe caching mechanism with support for ETag and Last-Modified headers.
-   **Firewall & Interference Detection:** Add a "Situational Awareness" module to detect corporate proxy interference and route around it.
-   **Proxy Support:** Add optional support for using proxies for requests.
-   **Results & Historical Data Adapters:** Restore or build adapters specifically for fetching race results, enabling the `Backtesting Engine` to function.

### Phase 3: The Megaphone (Advanced Data & UI)
This phase transitions the toolkit from a batch-processing scraper to a real-time, always-on analysis engine and provides a user-friendly interface.

Key Future Features:
- **Rich Terminal User Interface (TUI):** Evolve the current command-line output into a dynamic, human-friendly terminal dashboard using a library like `rich` or `textual`. (IN PROGRESS)
- **Interactive Web Frontend:** Implement the frontend module with a simple API and web-based dashboard.
- **"Always-On" Assistant Mode:** Implement the "Persistent Engine" to run the application in the background and provide real-time notifications for high-scoring race opportunities.
- **Flexible Data Exports:** Add a feature to export results to common formats like CSV and JSON to empower user-led analysis.
- **Powerful CLI:** Enhance run.py with more filters and features.
- **Machine-Readable Outputs:** Implement JSON and CSV exporters.
- **HTML Reports:** Generate clean, user-friendly HTML summaries.

### Phase 4: Intelligence & Analysis
This phase focuses on enriching the data, improving the scoring model, and delivering the results to the user.

-   **Advanced Timezone Handling:** Implement a robust system for UTC normalization and DST-safe timezone conversions.
-   **Smart Merging & Provenance:** Implement logic to merge race data from multiple sources and track the provenance of each data field.
-   **Hybrid Browser/HTTP Scraping:** Implement a "Playwright Bootstrap" mechanism to solve CAPTCHAs or handle complex logins, then pass the session to the faster `httpx` client.

---

### **Appendix A: The Master List of Archived Blueprints**

This is the definitive, comprehensive master list of all known, non-active adapter blueprints for this project, compiled from our legacy archives. This list serves as a strategic backlog for future data acquisition missions.

**Core Racecards (UK/US):**
*   `attheraces` (Restoration in Progress)
*   `drf` (Daily Racing Form - Concept Only)
*   `sportinglife`
*   `timeform`
*   `racingtv`
*   `tvg` (US Horse Racing)
*   `twinspires`

**Betting & Tote Exchanges:**
*   `betfair`
*   `bovada`
*   `oddsportal` (Note: A specialized repository exists for this adapter)
*   `paddypower`
*   `totesport`
*   `williamhill`

**International Racecards:**
*   `atg` (Sweden)
*   `entain` (UK/International)
*   `francegalop` (France)
*   `hkjc` (Hong Kong)
*   `turfcom` (Turkey)

**Data Providers:**
*   `sis` (Sports Information Services)

**Results & Historical Data:**
*   `skysports_results`
*   `attheraces_results`
