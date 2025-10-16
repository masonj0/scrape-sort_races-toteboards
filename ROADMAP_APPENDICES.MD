# Fortuna Faucet - Grand Strategy & Appendices

This document serves as the "Windows Experience Bible," dictating the path forward for all user-facing components and developer tooling.

---

## CAMPAIGN: The Windows Experience

**Objective:** To transform the project from a collection of scripts into a cohesive, professional-grade, and resilient native Windows application with an A+ operator experience.

~~### Phase 1: Critical (Self-Healing & Efficiency)~~~

~~-   **Port Conflict Resolution:** The `LAUNCH_FORTUNA.bat` script should be intelligent enough to detect if ports 8000 or 3000 are already in use. If they are, it should attempt to kill the stale processes to ensure a clean startup.~~
~~-   **Health Check Loop:** The arbitrary `timeout` delays in the launch script should be replaced with an intelligent loop that actively polls the backend's `/health` endpoint. The frontend and browser should only be launched after the backend is confirmed to be fully operational.~~
~~-   **Log Aggregation:** All output from the backend (`uvicorn`) and frontend (`npm run dev`) services should be automatically redirected to timestamped log files in a new `logs/` directory. This makes troubleshooting startup failures trivial.~~

~~### Phase 2: Enhanced UX (Faster & Clearer)~~~

~~-   **Parallel Installation:** The `INSTALL_FORTUNA.bat` script should be refactored to install the Python (`pip`) and Node.js (`npm`) packages in parallel, significantly cutting down the initial setup time.~~
~~-   **Unified Launch Dashboard:** The `LAUNCH_FORTUNA.bat` script should present a clean, unified "dashboard" that updates in real-time as each service starts, providing the operator with a clear, professional status display.~~
~~-   **Interactive Setup Wizard:** A new `setup_wizard.py` script should be created to guide the operator through creating their `.env` file, eliminating the error-prone process of manual creation and editing.~~
~~-   **Real-time CLI Monitor:** A new `fortuna_status_cli.py` script should be created using a library like `rich` to provide a continuous, real-time, "power user" view of the system's health and adapter status.~~

~~### Phase 3: Professional (GUI & Power User Tools)~~~

~~-   **Advanced GUI Monitor:** The `fortuna_monitor.py` should be completely overhauled into a professional, graphical command deck using Tkinter. It should be a multi-pane application for fetching, filtering, and analyzing race data.~~
~~-   **Historical Performance Graphs:** The new GUI monitor should include a "Performance" tab with historical graphs (using `matplotlib`) for key metrics like races fetched, success rate, and fetch duration.~~
~~-   **Data Export:** The GUI monitor should include a feature to export the current view of adapter statuses or performance data to a CSV file.~~

~~### Phase 4: Production-Grade Suite (Final Polish)~~~

~~-   **Architecturally Superior Scripts:** Replace the entire suite of `.bat` files with a new, production-grade set that is resilient, race-condition-free, and provides a superior operator experience with enhanced diagnostics and self-healing capabilities.~~
~~-   **Unified Command Console (`SERVICE_MANAGER.bat`):** Unify all individual scripts under a single, user-friendly, menu-driven service manager, providing a 'single pane of glass' for all common operations.~~

### Phase 5: Power User (Data Warehouse & Analysis)

-   **ETL Pipeline:** A new `python_service/etl.py` script should be created to extract data from the API, perform strict validation and transformation, and load it into a PostgreSQL data warehouse.
-   **Data Warehouse Schema:** The `pg_schemas/` directory should contain the SQL `CREATE TABLE` statements for the `historical_races` and `quarantined_races` tables.
-   **Automated Daily ETL:** The `fortuna_watchman.py` script should be enhanced to run the ETL process as the final step of its daily protocol.

---

## CAMPAIGN COMPLETE: The Windows Experience (Phases 1-4)

**Date of Completion:** 2025-10-15

**Summary:** This strategic campaign was a complete success. The operator's toolkit and user experience have been elevated from a collection of simple scripts to a cohesive, intelligent, and resilient A+ grade system. The core objectives have been met and exceeded.