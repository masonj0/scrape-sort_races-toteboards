# Paddock Parser V3

This project is a modern, robust, and scalable data analysis toolkit for global horse and greyhound racing. It is built on an API-First, 'Monolith Reimagined' architecture, designed for long-term stability and performance.

## Architectural Philosophy: The Four Pillars
Development is guided by a clear architectural philosophy centered on four pillars. This shared language allows us to prioritize our work and ensure a balanced application.
*   **The Brain (`scorer.py`):** The core analytical engine.
*   **The Guardian (`merger.py`, `pipeline.py`):** The systems that ensure data integrity.
*   **The Template (The `adapters/` module):** The patterns for resiliently acquiring data.
*   **The Face (`terminal_ui.py`, the API):** The interfaces that deliver value to the user.

## Usage

To run the application in interactive mode, use the following command:

```bash
python launch_paddock_parser.py
```

## Supported Data Sources
This project leverages a sophisticated, multi-source approach. The current V3-compliant adapter fleet includes (but is not limited to):
*   **Racing Post** (Hybrid JSON/HTML)
*   **FanDuel** (GraphQL API)
*   **SkySports**
*   **Timeform**
*   **Equibase**
*   **AtTheRaces**
