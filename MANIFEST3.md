# Fortuna Faucet: Operational Manifest

**Purpose:** To provide a complete, verified list of all satellite files critical to the project's operation, tooling, and strategic direction.

---

## 1.0 Project Tooling
*   `.gitignore` - Defines version control exclusions.
*   `convert_to_json.py` - The legacy script for creating AI-reviewable backups.
*   `create_fortuna_json.py` - The primary script for creating the Superbrain package.
*   `run_fortuna.bat` - The standardized launcher for the entire application.
*   `command_deck.py` - The internal Streamlit dashboard for real-time monitoring.
*   `fortuna_watchman.py` - The master orchestrator for autonomous operation.
*   `live_monitor.py` - The 'Third Pillar' tactical engine.
*   `chart_scraper.py` - The 'Second Pillar' results archive tool.
*   `results_parser.py` - The 'Carpenter' for parsing PDF chart data.
*   `python_service/adapters/betfair_greyhound_adapter.py`

## 2.0 Environment & Setup
*   `setup_windows.bat` - The whole-system Windows environment setup script.
*   `.env` - Configuration for environment variables.
*   `.env.example` - An example template for environment configuration.
*   `python_service/requirements.txt` - Python backend dependencies.

## 3.0 Strategic Blueprints
*   `README.md` - The primary public-facing document.
*   `ARCHITECTURAL_MANDATE.md` - Defines the final architectural vision.
*   `HISTORY.md` - The narrative history of the project.
*   `WISDOM.md` - The operational protocol for AI agents.
*   `ROADMAP_APPENDICES.md` - The definitive adapter backlog and intelligence leads.
*   [python_service/adapters/betfair_greyhound_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/betfair_greyhound_adapter.py)
*   [python_service/adapters/racing_and_sports_greyhound_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/racing_and_sports_greyhound_adapter.py)
*   [python_service/adapters/at_the_races_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/at_the_races_adapter.py)
*   [python_service/adapters/sporting_life_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/sporting_life_adapter.py)
*   [python_service/adapters/timeform_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/timeform_adapter.py)
*   [python_service/adapters/the_racing_api_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/the_racing_api_adapter.py)
*   [web_platform/frontend/next.config.mjs](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/next.config.mjs)
*   [web_platform/frontend/postcss.config.js](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/postcss.config.js)
*   [web_platform/frontend/.env.local.example](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/.env.local.example)
*   [web_platform/frontend/src/components/RaceCard.tsx](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/components/RaceCard.tsx)
*   [web_platform/frontend/src/components/LiveRaceDashboard.tsx](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/components/LiveRaceDashboard.tsx)
*   [web_platform/frontend/src/app/Providers.tsx](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/web_platform/frontend/src/app/Providers.tsx)