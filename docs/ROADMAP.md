# ROADMAP.md: The Phased Implementation Roadmap

This is the step-by-step plan to build this new project from scratch.

## Phase 1: The Foundation

*   **Repo Setup:** Create the new `next-gen` repository.
*   **Scaffolding:** Create the complete directory structure outlined in the blueprint.
*   **Dockerization:** Create the `docker-compose.yml` file and the individual `Dockerfile` for each service. The goal is to be able to run `docker-compose up` and have all three (empty) services start correctly.
*   **The First Adapter:** Implement the `FanDuelGraphQLAdapter` inside the Python Orchestrator. This will be our first, flagship data source.
*   **The Forager Skeleton:** Build a basic "Hello World" version of the Go Forager that the Python Orchestrator can successfully call.

## Phase 2: Core Logic & Data Persistence

*   **The Scorer:** Implement the initial `V2Scorer` logic inside the Python Orchestrator's analysis module.
*   **The Database:** Implement the `DatabaseManager` (using SQLite for simplicity) to store the results of the scoring runs. This is the foundation for our historical data.
*   **The API Contract:** Formally define the API that the Orchestrator will expose for the Frontend to consume.

## Phase 3: Bringing the Data to Life

*   **The Frontend:** Build the TypeScript "Town Crier" application. It should call the Orchestrator's API and display the scored races in a simple, clean table.
*   **Legacy Code Migration:** Now, and only now, we can begin to carefully borrow and adapt the tested parsing logic from our old project's adapters (Equibase, RacingPost, GreyhoundRecorder) to quickly expand our data sources.
