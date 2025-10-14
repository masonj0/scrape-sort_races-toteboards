# Fortuna Faucet

**A professional-grade, autonomous intelligence engine for horse racing analysis, delivered as a native Windows Desktop Application.**

---

## Fortuna: The Windows Native Edition

This project has evolved into a true, professional-grade Windows application. The primary user experience is managed through a system tray icon, a native monitoring GUI, and a suite of powerful batch scripts.

**For all user-facing documentation, including installation and operation, please see the official operator's manual:**

### [>> Go to the Windows Operator's Manual (README_WINDOWS.md)](README_WINDOWS.md)

---

## Project Philosophy & Architecture

This project adheres to a strict set of architectural and operational principles. To understand the soul of this machine, consult the following sacred texts:

-   **[The Grand Strategy (ROADMAP_APPENDICES.MD)](ROADMAP_APPENDICES.MD):** The "Windows Experience Bible" that dictates our path forward.
-   **[The Genesis Story (HISTORY.MD)](HISTORY.MD):** The complete history of the project's evolution.
-   **[The Architectural Blueprint (PSEUDOCODE.MD)](PSEUDOCODE.MD):** The comprehensive pseudocode blueprint for the entire system.

## For Developers

The codebase is a three-layered architecture:

1.  **The Engine Room (The Windows Service):** A persistent Python backend (`python_service/`).
2.  **The Cockpit (The Electron Shell):** A native desktop application wrapper (`electron/`).
3.  **The Command Deck (The Next.js UI):** A real-time dashboard (`web_platform/frontend/`).