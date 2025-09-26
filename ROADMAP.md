# ROADMAP V3.0

## Phase 1: "The Grand Fleet" (Immediate Priority)
*   **Objective:** Achieve data dominance by integrating our backlog of proven, high-value adapters.
*   **Deliverables:**
    *   Refactor and integrate the `TVGAdapter`.
    *   Refactor and integrate the `BetfairExchangeAdapter`.
    *   Refactor and integrate the `OddsAPIAdapter`.
*   **Success Metric:** The `DataSourceOrchestrator`'s production fleet is doubled, dramatically increasing the volume and variety of data for the "Jealousy Engine."

## Phase 2: "The Cockpit & The Crier" (The User Experience)
*   **Objective:** Build the first tangible, user-facing manifestations of our "Impossible Dream."
*   **Deliverables:**
    *   **The Cockpit:** A V1 React-based dashboard that consumes our API and displays the live tipsheet, based on the `webapp_pseudocode.md` design document.
    *   **The Crier:** A V1 `SlackAlerter` that sends real-time notifications for qualified races, based on the "Operation: Town Crier" directive.
*   **Success Metric:** The project has a live, graphical user interface and a real-time alerting system.

## Phase 3: "The Dojo" (The Quality Gate)
*   **Objective:** Harden our test suite and accelerate our development velocity.
*   **Deliverables:**
    *   Create and integrate a `SampleAdapter` for predictable, positive-path testing.
    *   Create and integrate a `MockFailureAdapter` for testing our system's resilience to errors.
*   **Success Metric:** Our `pytest` suite can run comprehensive integration tests without relying on slow and unpredictable live network calls.