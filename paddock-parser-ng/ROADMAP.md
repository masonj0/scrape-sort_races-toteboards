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

### Phase 1: Foundation & Professional CLI (Complete)
This phase focused on unifying the project structure, stabilizing the core components, and building a flexible command-line interface.

-   **Project Unification:** Migrated to a standard `src` layout.
-   **Core Adapters:** Restored and tested the `SkySportsAdapter` and `FanDuelAdapter`.
-   **Professional CLI:** Implemented a powerful CLI using `argparse`, allowing for configurable pipeline execution.
-   **Async Pipeline:** Refactored the core pipeline to be asynchronous, supporting both sync and async adapters.

### Phase 2: The Professional Fetching Engine
This phase focuses on making our data gathering dramatically more resilient and intelligent.

-   **User-Agent & Fingerprint Rotation (Complete):** Implement rotation of User-Agents and other browser fingerprints to avoid blocking.
-   **Intelligent Retries & Backoff (Complete):** Implement a resilient `get` method with exponential backoff for 429/5xx errors.
-   **Advanced Caching:** Implement a crash-safe caching mechanism with support for ETag and Last-Modified headers.
-   **Firewall & Interference Detection:** Add a "Situational Awareness" module to detect corporate proxy interference and route around it.
-   **Proxy Support:** Add optional support for using proxies for requests.

### Phase 3: Advanced Data & Persistent Engine
This phase transitions the toolkit from a batch-processing scraper to a real-time, always-on analysis engine.

-   **Smart Merging & Provenance:** Implement logic to merge race data from multiple sources and track the provenance of each data field.
-   **Persistent Engine:** Implement the "always-on" engine mode (`--persistent` flag) for continuous monitoring and analysis.
-   **Real-Time Data via WebSockets:** Add support for WebSocket adapters to receive real-time odds data.
-   **Hybrid Browser/HTTP Scraping:** Implement a "Playwright Bootstrap" mechanism to solve CAPTCHAs or handle complex logins, then pass the session to the faster `httpx` client.

### Phase 4: Intelligence & User Interface
This phase focuses on enriching the data, improving the scoring model, and delivering the results to the user.

-   **Advanced Timezone Handling:** Implement a robust system for UTC normalization and DST-safe timezone conversions.
-   **Machine-Readable Outputs:** Add support for versioned JSON and CSV outputs.
-   **Web Frontend:** Develop a simple web frontend using the `FastAPI` module to display results and control the application.
-   **Advanced CLI Controls:** Add more granular CLI flags for filtering, grouping, and output formatting.

---

## 3. Archived Adapter Blueprints

The following list is a supplement to the roadmap, recovered from legacy project archives. It will be used to inform the selection of future missions.

**Core Racecards (UK/US):**
*   `attheraces`
*   `drf` (Daily Racing Form)
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
*   `turfcom` (Turkey)

**Data Providers:**
*   `sis` (Sports Information Services)

**Results & Historical Data:**
*   `skysports_results`
*   `attheraces_results`

---

## The "Monolith Reimagined" Architecture

The project uses a "Monolith Reimagined" architecture, building a single, unified Python application while structuring the internal code to mirror a microservices design. This facilitates easy development now and a potential migration to a true microservices architecture in the future.

-   **Python Orchestrator:** The core application for orchestration and analysis.
-   **Forager Module (`src/paddock_parser/forager/`):** A dedicated placeholder for high-performance data fetching logic.
-   **Frontend Module (`src/paddock_parser/frontend/`):** A dedicated placeholder for the web server and API logic.
