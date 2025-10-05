# The Fortuna Faucet Architectural Mandate

## The Prime Directive: The Two-Pillar System

The project's architecture is a lean, hyper-powerful, two-pillar system chosen for its clarity, maintainability, and performance.

## Pillar 1: The Asynchronous Python Backend

The backend is a modern, asynchronous service built on **FastAPI**. Its architecture includes:

1.  **The `OddsEngine`:** A central, async orchestrator for data collection.
2.  **The Resilient `BaseAdapter`:** An abstract base class providing professional-grade features.
3.  **The Adapter Fleet:** A modular system of 'plugin' adapters for data sources.
4.  **Pydantic Data Contracts:** Strict, validated Pydantic models for data integrity.
5.  **The `TrifectaAnalyzer` (Intelligence Layer):** A dedicated module for scoring and qualifying opportunities.

## Pillar 2: The TypeScript Frontend

The frontend is a modern, feature-rich web application built on **Next.js** and **TypeScript**.