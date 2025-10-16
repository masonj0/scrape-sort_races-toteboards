# Fortuna Faucet - Architectural Mandate (v3.0)

This document codifies the architectural laws and philosophical principles that govern the Fortuna Faucet kingdom. Adherence to this mandate is non-negotiable for all development.

---

## The Prime Directive: A Professional, Resilient System

The ultimate goal of this project is to be a professional-grade, A+ intelligence engine. This is achieved through three core pillars:

1.  **Rigid Standardization:** Code should be consistent and predictable. Shared logic must be centralized. Common patterns must be enforced, not merely suggested.
2.  **Resilience Engineering:** The system must be self-healing and gracefully handle the failure of its individual components. We do not simply handle errors; we build a system that anticipates and survives them.
3.  **Developer Clarity:** The codebase must be easy to understand, maintain, and extend. Code should be self-documenting, and its intent should be obvious.

---

## The Law of the Adapters: The `BaseAdapterV3` Pattern

All new data adapters **MUST** inherit from the `BaseAdapterV3` abstract base class. This is the cornerstone of our standardization and resilience strategy.

The `BaseAdapterV3` enforces a strict separation of concerns:

1.  **`_fetch_data(self, date)` -> `Any`:** This method's **only** responsibility is to perform network operations and retrieve raw data (e.g., HTML, JSON). It should contain no parsing logic.
2.  **`_parse_races(self, raw_data)` -> `list[Race]`:** This method's **only** responsibility is to parse the raw data provided by `_fetch_data` into a list of `Race` objects. It must be a pure function with no side effects or network calls.

The public-facing `get_races()` method is provided by the base class and **MUST NOT** be overridden. It orchestrates the fetch-then-parse pipeline, ensuring that all adapters behave identically from the engine's perspective.

This pattern guarantees that every adapter in our fleet is consistent, predictable, and easy to test.

---

## The Law of the Engine: Orchestrate, Don't Participate

The `OddsEngine` is the central orchestrator. Its responsibilities are:

-   To manage the fleet of active adapters.
-   To execute all adapter fetches in parallel.
-   To gracefully handle the failure of any individual adapter without halting the entire process.
-   To perform the deduplication and merging of race data from multiple sources.
-   To manage the caching layer (Redis).

The engine should remain agnostic to the internal workings of any specific adapter. It interacts only with the standardized interface provided by `BaseAdapterV3`.

---

## The Law of the Core Texts: Maintain the Truth

The project's core documentation is not optional. It is the living memory and strategic guide of the kingdom.

-   **`ROADMAP_APPENDICES.MD`:** The Grand Strategy must be kept current. Completed objectives must be marked as such.
-   **`HISTORY.MD`:** Significant architectural shifts and completed campaigns must be chronicled.
-   **`PSEUDOCODE.MD`:** The architectural blueprint must be updated to reflect major changes to the system's design.
-   **Manifests (`MANIFEST*.md`):** All new files must be added to the appropriate manifest to ensure the integrity of the archival system.


---

## The Final Law: The Law of the True Scribe

**Effective Date:** 2025-10-15

**Verdict:** The system of manually maintained manifest files (`MANIFEST.md`, `MANIFEST2.md`, `MANIFEST3.md`) is hereby declared a catastrophic failure and is **permanently deprecated**.

**The New Law:** The one and only method for generating the project's `FORTUNA_ALL` archives is the `ARCHIVE_PROJECT.py` script. This 'True Scribe' is the single, automated source of truth. It programmatically scans and categorizes the entire kingdom, ensuring a perfect, complete, and uncorrupted archive is generated every time.

All previous archival scripts (`create_fortuna_json.py`, `MANAGE_MANIFESTS.py`) are not to be used under any circumstances.