# Checkmate V8: Project Manifest

**Purpose:** To categorize all top-level files and directories, distinguishing between the active **CORE** system and **LEGACY** components slated for archival.

---

## CORE ARCHITECTURE (Penta-Hybrid)

*   `.env`: **CORE** - Centralized configuration for all platforms.
*   `ARCHITECTURAL_MANDATE.md`: **CORE** - The project's strategic blueprint.
*   `HISTORY.md`: **CORE** - The project's official, running log of major events.
*   `README.md`: **CORE** - The primary entry point for new developers.
*   `STATUS.md`: **CORE** - The live status report for the project.
*   `build_python_service.py`: **CORE** - Deprecated build script, to be replaced by a launcher build script.
*   `launcher.py`: **CORE** - The new master orchestrator for the entire system.
*   `pyproject.toml`: **CORE** - Configuration for Python tooling (Ruff).
*   `tipsheet_generator.py`: **CORE** - The production-ready, standalone tipsheet generator.
*   `desktop_app/`: **CORE** - The C# Command Deck.
*   `python_service/`: **CORE** - The Python Collection Corps.
*   `rust_engine/`: **CORE** - The Rust Analysis Core.
*   `setup_windows.bat`: **CORE** - The environment setup script.
*   `shared_database/`: **CORE** - The central SQLite database schemas.
*   `vba_source/`: **CORE** - The source code for the Excel Familiar Frontend.
*   `web_platform/`: **CORE** - The TypeScript Live Cockpit.

---

## LEGACY & HISTORICAL ARTIFACTS

*   All other files and directories not listed in CORE are considered LEGACY and are candidates for archival in the next phase of "The Great Simplification."