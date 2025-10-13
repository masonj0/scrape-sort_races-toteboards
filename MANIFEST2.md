# Fortuna Faucet - Backend Manifest (Part 2)

This manifest lists all core backend services, utilities, and the entire adapter fleet.

## Core Services

* python_service/api.py
* python_service/engine.py
* python_service/analyzer.py
* python_service/live_monitor.py

## Data Models & Configuration

* python_service/config.py
* python_service/models.py
* python_service/models_v3.py

## Production Hardening & ETL

* python_service/health.py
* python_service/cache_manager.py
* python_service/middleware/error_handler.py
* python_service/etl.py

## Adapter Architecture

* python_service/adapters/base.py
* python_service/adapters/base_v3.py
* python_service/adapters/utils.py

## Adapter Fleet

* python_service/adapters/at_the_races_adapter.py
* python_service/adapters/betfair_adapter.py
* python_service/adapters/betfair_datascientist_adapter.py
* python_service/adapters/betfair_greyhound_adapter.py
* python_service/adapters/fanduel_adapter.py
* python_service/adapters/gbgb_api_adapter.py
* python_service/adapters/greyhound_adapter.py
* python_service/adapters/harness_adapter.py
* python_service/adapters/oddschecker_adapter.py
* python_service/adapters/racing_and_sports_adapter.py
* python_service/adapters/sporting_life_adapter.py
* python_service/adapters/the_racing_api_adapter.py
* python_service/adapters/timeform_adapter.py
* python_service/adapters/tvg_adapter.py

# Added by Operation: Complete the Royal Blueprints
pg_schemas/historical_races.sql
pg_schemas/quarantine_races.sql
python_service/analyzer.py
python_service/api.py
python_service/cache_manager.py
python_service/checkmate_service.py
python_service/engine.py
python_service/etl.py
python_service/health.py
python_service/windows_service_wrapper.py
python_service/adapters/at_the_races_adapter.py
python_service/adapters/base_v3.py
python_service/adapters/betfair_datascientist_adapter.py
python_service/middleware/error_handler.py
src/paddock_parser/api/main.py
src/paddock_parser/database/manager.py
src/paddock_parser/ui/terminal_ui.py
src/paddock_parser/utils/browser.py
src/paddock_parser/utils/honeypot.py
tests/test_analyzer.py
tests/test_api.py
tests/test_engine.py
tests/adapters/test_gbgb_api_adapter.py
tests/adapters/test_greyhound_adapter.py
tests/adapters/test_the_racing_api_adapter.py

