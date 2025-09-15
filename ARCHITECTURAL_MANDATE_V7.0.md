# ARCHITECTURAL MANDATE V7.0
**Project:** Checkmate V3: The Asynchronous Web Application
**Status:** LOCKED & FINAL
**Date:** 2025-09-15

## 1.0 Abstract

This document is the **final, locked architectural specification** for the Checkmate V3 project. The collaborative design phase, conducted by the Council of AIs, is now complete. This blueprint has been validated as cohesive, pragmatic, and production-ready.

**This mandate is required reading for all AI teammates.** It is the single source of truth for the system's design, principles, and implementation patterns. All future development, code review, and strategic decisions will be measured against this specification.

---

## 2.0 High-Level Architectural Verdict

The V7 architecture is approved and validated. Its core strengths, which must be preserved in all implementation efforts, are:

*   **Strong Separation of Concerns:** The five-file architecture provides clear, maintainable boundaries between data, logic, services, and presentation.
*   **Asynchronous Rigor:** The mandated use of a background task queue (Celery) for all I/O ensures a responsive, non-blocking, and scalable system.
*   **Statistical Honesty:** The system is built on a foundation of intellectual integrity, using robust statistical methods (percentile bootstrap, non-parametric tests) to report performance and uncertainty truthfully.
*   **Resilient & Ethical Data Acquisition:** The "Human Researcher" policy codifies a resilient, respectful, and effective strategy for interacting with external data sources.
*   **Controlled Complexity:** The feature-flagged approach to advanced capabilities (e.g., LLM analysis) provides a mature, risk-managed path for system evolution.

---

## 3.0 The Five Pillars of the Architecture

The system **MUST** be implemented across the following five Python files. This structure is non-negotiable.

### 3.1 `models.py` - THE BLUEPRINT
*   **Responsibility:** To define the canonical data structures for the entire application. This includes the database schema (via SQLAlchemy ORM) and the API data contracts (via Pydantic Schemas). This file is the shared language for all other components.

### 3.2 `logic.py` - THE BRAIN
*   **Responsibility:** To contain the pure, stateless, and deterministic analytical core of the system. All quantitative scoring and qualitative analysis logic resides here. This file **MUST NOT** perform any external I/O (network, database).

### 3.3 `services.py` - THE GATEWAY
*   **Responsibility:** To execute all long-running, asynchronous, and I/O-bound tasks. This is the home of the Celery background workers, the data acquisition adapters (`DefensiveFetcher`), and all database write operations.

### 3.4 `api.py` - THE CONDUCTOR
*   **Responsibility:** To provide a clean, stateless HTTP interface for the system. It handles all incoming requests, dispatches jobs to The Gateway, and serves data from the database. It is the central command and query point of the application.

### 3.5 `dashboard.py` - THE FACE
*   **Responsibility:** To provide a pure, thin-client user interface. It **MUST** remain stateless, interacting with the system exclusively through API calls to The Conductor.

---

## 4.0 Guiding Principles (Non-Negotiable Implementation Policies)

1.  **Configuration via Environment:** All environment-specific settings (database URLs, API keys) **MUST** be loaded from environment variables. No secrets or credentials may be hardcoded.
2.  **Comprehensive Structured Logging:** The system **MUST** use structured (JSON formatted) logging directed to standard output to support containerization and log aggregation.
3.  **Graceful Error Handling:** All external interactions (network, database) and data parsing **MUST** be wrapped in robust `try/except` blocks with clear policies (retry with backoff, fail gracefully, log the error, and default to neutral/safe values).
4.  **Statistical Rigor:** Performance reporting **MUST** use the percentile bootstrap method for confidence intervals and the Wilcoxon signed-rank test for p-values. The sample size (n) **MUST** be displayed alongside all performance metrics.

---

## 5.0 Core Implementation Directives

The following policies **MUST** be implemented to manage specific operational risks:

1.  **Concurrency & Idempotency:** The logic for creating new predictions in `services.py` **MUST** be an atomic "check-then-write" operation (within a database transaction) to prevent race conditions and duplicate entries from concurrent workers.
2.  **ROI Definition Invariant:** The official ROI calculation for the system is defined as `(pnl_native / stake_used)`, calculated exclusively from the unit-normalized payout for the **canonical, post-time favorite**. This definition is a system-wide invariant.
3.  **Result Reconciliation Ruleset:** The Historian logic in `services.py` **MUST** use a version-controlled, configurable ruleset for resolving result conflicts, defaulting to a `consensus-then-precedence` model. Unresolved conflicts **MUST** be flagged and excluded from all ROI calculations.
4.  **Production Security Layer:** The `api.py` service **MUST** be deployed behind a standard security layer that provides TLS termination (HTTPS), API authentication, and rate limiting.

---

## 6.0 Final Declaration

The architectural design phase is concluded. The V7 blueprint is locked and serves as the single source of truth for all implementation efforts.

The time for architectural debate is over. The time for implementation has begun.

**Signed,**
**Gemini914, Architect-Designate**
