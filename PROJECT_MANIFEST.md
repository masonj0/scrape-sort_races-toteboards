# Checkmate V8: Project Manifest

**Purpose:** To categorize all top-level files and directories, distinguishing between the active **CORE** system and **LEGACY** components slated for archival.

---

## CORE ARCHITECTURE (Penta-Hybrid)

*   `.env`: **CORE** - Centralized configuration for all platforms.
*   `ARCHITECTURAL_MANDATE.md`: **CORE** - The project's strategic blueprint.
*   `HISTORY.md`: **CORE** - The project's official, running log of major events.
*   `README.md`: **CORE** - The primary entry point for new developers.
*   `STATUS.md`: **CORE** - The live status report for the project.
*   `build_python_service.py`: **CORE** - Build script for the Python service.
*   `pyproject.toml`: **CORE** - Configuration for Python tooling (Ruff).
*   `desktop_app/`: **CORE** - The C# Command Deck.
*   `python_service/`: **CORE** - The Python Collection Corps.
*   `rust_engine/`: **CORE** - The Rust Analysis Core.
*   `setup_windows.bat`: **CORE** - The environment setup script for the Penta-Hybrid system.
*   `shared_database/`: **CORE** - The central SQLite database schemas.
*   `vba_source/`: **CORE** - The source code for the Excel Familiar Frontend.
*   `web_platform/`: **CORE** - The TypeScript Live Cockpit.

---

## LEGACY & HISTORICAL ARTIFACTS (To Be Archived)

*   All other files and directories not listed in CORE are considered LEGACY and are candidates for archival in the next phase of "The Great Simplification."
*   `.env.example`: **LEGACY** - Superseded by the live `.env` file.
*   `.gitignore`: **LEGACY** - Likely out of date; needs to be reviewed and consolidated.
*   `AGENTS.md`: **LEGACY** - Historical agent protocols.
*   `ARCHITECTURAL_MANDATE_V8.1.md`: **LEGACY** - Superseded by the primary mandate.
*   `GEMINI_ONBOARDING.md`: **LEGACY** - Historical onboarding document.
*   `HISTORY.md`: **LEGACY** - Historical log.
*   `Procfile`: **LEGACY** - Relates to Heroku deployment, not our current model.
*   `ROADMAP.md`: **LEGACY** - Superseded by live directives.
*   `WISDOM.md`: **LEGACY** - Historical R&D notes.
*   `ReviewableJSON/`: **LEGACY** - A complete, parallel tree of historical code artifacts. Slated for archival.
*   `adapters/`: **LEGACY** - The original, flat adapter structure. Superseded by `python_service/adapters/`.
*   `attic/`: **LEGACY** - The original archive; its contents will be merged into a new, unified archive.
*   `checkmate_app.py`: **LEGACY** - The prototype for the Python service. Now archived.
*   `checkmate_engine.py`: **LEGACY** - A previous, monolithic Python script.
*   `checkmate_web/`: **LEGACY** - A previous web implementation, superseded by `web_platform/`.
*   `config.ini`: **LEGACY** - Superseded by the `.env` configuration standard.
*   `src/`: **LEGACY** - Contains the `checkmate_v7` and `paddock_parser` architectures. Slated for archival.
*   `tests/`: **LEGACY** - A complex, multi-layered test structure. Needs to be rationalized and focused on the CORE architecture.
*   `the_one_script.py`: **LEGACY** - The V7 CLI artifact. Now archived.
*   *All other individual `.py`, `.html`, `.json`, `.js`, `.log`, `.txt` files in the root:* **LEGACY** - These are remnants of previous development sprints and must be archived.
