# The Checkmate Architectural Mandate (V2)

## The Prime Directive: The Two-Pillar System

The project's architecture is a lean, hyper-powerful, two-pillar system: The **"Ultimate Solo."** This design was chosen for its clarity, maintainability, and performance, representing the hard-won victory over the complexity of previous multi-language architectures.

## Pillar 1: The Asynchronous Python Backend

The backend is a modern, asynchronous service built on **FastAPI**. Its architecture is defined by the principles in `checkmate_pseudocode.md.txt` and includes:

1.  **The `OddsEngine`:** A central, async orchestrator responsible for managing the data collection lifecycle.
2.  **The Resilient `BaseAdapter`:** A sophisticated abstract base class that provides all adapters with built-in, professional-grade features like `httpx` connection pooling, automatic retries with exponential backoff, and standardized error handling.
3.  **The Adapter Fleet:** A modular system of 'plugin' adapters that inherit from the `BaseAdapter`, each responsible for a single data source.
4.  **Pydantic Data Contracts:** Strict, validated Pydantic models are used for all data, ensuring type safety and data integrity throughout the entire application.

## Pillar 2: The Ultimate TypeScript Frontend

The frontend is a modern, feature-rich web application built on **Next.js** and **TypeScript**. It provides the complete, production-grade operational dashboard for the end-user.