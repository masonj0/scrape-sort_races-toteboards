# Fortuna Faucet - Backend Manifest (Part 2)

This manifest lists all core backend services, utilities, and the entire adapter fleet.

## Core Services

*   [python_service/api.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/api.py)
*   [python_service/engine.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/engine.py)
*   [python_service/analyzer.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/analyzer.py)
*   [python_service/live_monitor.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/live_monitor.py)

## Data Models & Configuration

*   [python_service/config.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/config.py)
*   [python_service/models.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/models.py)
*   [python_service/models_v3.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/models_v3.py)

## Production Hardening & ETL

*   [python_service/health.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/health.py)
*   [python_service/cache_manager.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/cache_manager.py)
*   [python_service/middleware/error_handler.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/middleware/error_handler.py)
*   [python_service/etl.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/etl.py)

## Adapter Architecture

*   [python_service/adapters/base.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/base.py)
*   [python_service/adapters/base_v3.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/base_v3.py)
*   [python_service/adapters/utils.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/utils.py)

## Adapter Fleet

*   [python_service/adapters/at_the_races_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/at_the_races_adapter.py)
*   [python_service/adapters/betfair_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/betfair_adapter.py)
*   [python_service/adapters/betfair_datascientist_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/betfair_datascientist_adapter.py)
*   [python_service/adapters/betfair_greyhound_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/betfair_greyhound_adapter.py)
*   [python_service/adapters/fanduel_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/fanduel_adapter.py)
*   [python_service/adapters/gbgb_api_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/gbgb_api_adapter.py)
*   [python_service/adapters/greyhound_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/greyhound_adapter.py)
*   [python_service/adapters/harness_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/harness_adapter.py)
*   [python_service/adapters/oddschecker_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/oddschecker_adapter.py)
*   [python_service/adapters/racing_and_sports_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/racing_and_sports_adapter.py)
*   [python_service/adapters/sporting_life_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/sporting_life_adapter.py)
*   [python_service/adapters/the_racing_api_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/the_racing_api_adapter.py)
*   [python_service/adapters/timeform_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/timeform_adapter.py)
*   [python_service/adapters/tvg_adapter.py](https://raw.githubusercontent.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/python_service/adapters/tvg_adapter.py)
