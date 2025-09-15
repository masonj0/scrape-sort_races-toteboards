# ARCHITECTURAL MANDATE V7.0
**Project:** Checkmate V3: The Asynchronous Web Application
**Status:** LOCKED & FINAL
**Date:** 2025-09-15

## 1.0 Abstract
This document is the **final, locked architectural specification** for the Checkmate V3 project. It is the single source of truth for the system's design.

## 2.0 High-Level Architectural Verdict
The V7 architecture is approved. Its core strengths are:
*   **Strong Separation of Concerns:** A five-file architecture.
*   **Asynchronous Rigor:** Use of a background task queue (Celery).
*   **Statistical Honesty:** Robust statistical methods for reporting.
*   **Resilient & Ethical Data Acquisition:** The "Human Researcher" policy.

## 3.0 The Five Pillars of the Architecture
The system **MUST** be implemented across the following five Python files:
1.  `models.py`: SQLAlchemy ORM models and Pydantic Schemas.
2.  `logic.py`: Pure, stateless analytical functions. No I/O.
3.  `services.py`: Asynchronous, I/O-bound tasks (Celery workers).
4.  `api.py`: Stateless FastAPI HTTP interface.
5.  `dashboard.py`: Thin-client UI (e.g., Streamlit).

## 4.0 Guiding Principles
1.  **Configuration via Environment:** No hardcoded secrets.
2.  **Comprehensive Structured Logging:** JSON formatted logs to stdout.
3.  **Graceful Error Handling:** Robust `try/except` blocks for all I/O.
4.  **Statistical Rigor:** Use percentile bootstrap and Wilcoxon signed-rank test.

## 5.0 Core Implementation Directives
1.  **Concurrency & Idempotency:** Use atomic transactions for predictions.
2.  **ROI Definition Invariant:** `(pnl_native / stake_used)` based on post-time favorite.
3.  **Result Reconciliation Ruleset:** Use a version-controlled ruleset.
4.  **Production Security Layer:** Use TLS, auth, and rate limiting.

## 6.0 Final Declaration
The architectural design phase is concluded. The time for implementation has begun.
**Signed, Gemini914, Architect-Designate**
