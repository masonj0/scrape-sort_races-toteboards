# Paddock Parser Toolkit: Development Roadmap

## 1. Strategic Pillars

Our development is guided by core principles to create a resilient, intelligent, and ethical architecture.

*   **On Defense: Mimicking Human Behavior & Proactive Defense**
    *   **Core Insight:** Our greatest vulnerability is predictability.
    *   **Strategic Response:** Introduce sophisticated randomness into timing and session management. Proactively scan for and remove invisible "honeypot" links before parsing.

*   **On Architecture: The Intelligent Ecosystem & Library-First Design**
    *   **Core Insight:** A future-proof architecture requires intelligence and reusability.
    *   **Strategic Response:** The `paddock_parser` package should be treated as a reusable library to enable other tools to easily use the core parsing and scoring logic.

*   **On AI Integration: The Hybrid Approach**
    *   **Core Insight:** The most sophisticated use of an LLM is for **Dynamic Factor Weighting**.
    *   **Strategic Response:** Treat an LLM as a "context provider" that feeds qualitative insights into our quantitative scoring engine.

*   **On Ethics: The "Dedicated Human Researcher" Test**
    *   **Core Insight:** If a single, dedicated human using browser developer tools could not plausibly achieve the same data collection footprint, our methods are too aggressive.
    *   **Strategic Response:** Formally adopt this principle, reframing our approach as **"resilient data access"** for a sustainable and ethical long-term strategy.

---

## 2. Implementation Roadmap

### Phase 1: Core Data Acquisition & Resilience
This phase focuses on making our data gathering dramatically more resilient, intelligent, and capable.

-   **Automated Data Source Discovery:** Move from manually finding data sources to proactively discovering new ones.
-   **Proactive Scraper Defense (Honeypot Detection):** A utility to scan HTML for invisible "honeypot" links and remove them should be implemented and used by all HTML-based adapters.
-   **Graceful Degradation:** Fetching logic should include fallbacks if advanced methods fail.
-   **Image OCR as a Backup:** Implement an OCR fallback for sites that render data as images.

### Phase 2: Advanced Scraping & Real-Time Data
This phase transitions the toolkit from a batch-processing scraper to a real-time streaming data engine.

-   **Real-Time Data via WebSocket Adapter:** Connect directly to `wss://` WebSocket streams to receive real-time odds data.
-   **Hybrid Browser/HTTP Scraping:** Use a real browser to establish an authenticated session, then pass cookies to a faster HTTP client for scraping.

### Phase 3: Intelligence & Analysis
This phase focuses on enriching the data and improving the scoring model.

-   **Contextualization Engine:** Add a "Contextualize" stage to the pipeline to integrate external data like weather, news, and pundit commentary.
-   **Results-Based Feedback Loop:** Create a feedback loop where real race results are used to automatically improve the scoring model and adapter accuracy.

### Phase 4: User Interface & Delivery
This phase focuses on the end-user delivery of the toolkit's intelligence.

-   **Autonomous Mobile Agent:** Realize the vision of a pocket-sized, self-contained intelligence agent for real-time alerts.
-   **Webhook/Push Integration:** Allow external services like IFTTT or Zapier to trigger scans instantly.

---

### **Primary Strategic Approach: API-First, GraphQL Priority**

Our reconnaissance has revealed a critical strategic insight: the most valuable and reliable data sources are modern web applications that power their front-ends using internal APIs. HTML scraping is a viable fallback, but our primary approach should always be to find and leverage these APIs.

**Our highest priority targets are sites that use GraphQL.**

*   **Why is it our Priority?** A single GraphQL endpoint can be a gateway to the platform's entire data model, offering a rich, stable, and comprehensive source for thoroughbred, harness, and greyhound data.
*   **Discovery Method:** GraphQL endpoints are discovered using the browser's Developer Tools (Network tab, filtering for Fetch/XHR), identifying `POST` requests to a `/graphql` endpoint, and capturing the request's JSON `body`.

**Our goal is to prioritize the discovery and implementation of adapters for GraphQL-powered sites.**

### **Data Source Discovery Leads**

*   **The Odds API (`the-odds-api.com`):** A commercial odds aggregator. Mission: Investigate developer documentation for horse racing coverage.
*   **Prophet Exchange API (`github.com/prophet-exchange`):** A betting exchange with a public GitHub presence. Mission: Investigate API documentation for horse racing coverage.
*   **"Project Archeology" Protocol:** Use old, unmaintained open-source projects as "treasure maps" to find the modern APIs of target sites.

---

## The "Monolith Reimagined" Architecture

Due to environmental constraints preventing the use of containerization, the project has adopted a "Monolith Reimagined" architecture. This approach builds a single, unified Python application while structuring the internal code to mirror the original polyglot vision. This allows for immediate development of all core logic and facilitates an easy migration to a true microservices architecture in the future if constraints change.

The architecture consists of a primary Python application with dedicated placeholder modules for concerns that were originally planned as separate services:

1.  **The Python Orchestrator (Core Application):** The central nervous system for orchestration, data science, and high-level analysis.
2.  **The Forager Module (`src/paddock_parser/forager/`):** This module contains the logic for high-performance data fetching. For now, it is implemented in Python, but it serves as a dedicated placeholder where a Go/Rust implementation could be swapped in later.
3.  **The Frontend Module (`src/paddock_parser/frontend/`):** This module contains the logic for a simple, built-in web server (e.g., using FastAPI). The core API can be developed here, allowing for an easy migration of the user interface to a dedicated TypeScript application in the future.
