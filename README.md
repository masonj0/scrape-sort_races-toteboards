# Paddock Parser V3

This project is a modern, robust, and scalable data analysis toolkit for global horse and greyhound racing. It is built on an API-First, 'Monolith Reimagined' architecture, designed for long-term stability and performance.

## Installation

To get started, clone the repository and install the package in editable mode. This will install all necessary dependencies and make the command-line tools available in your environment.

```bash
git clone <repository_url>
cd <repository_directory>
pip install -e .
```

## Usage

Once installed, you can run the application's different interfaces using the following commands from anywhere in your terminal:

**To launch the interactive terminal UI:**
```bash
paddock_parser_ui
```

**To launch the web-based dashboard:**
```bash
paddock_parser_dashboard
```

---

## Architectural Philosophy: The Four Pillars

The development of Paddock Parser V3 is guided by a clear architectural philosophy centered on four distinct pillars. This shared language allows us to prioritize our work and ensure a balanced, robust application.

*   **The Brain (`scorer.py`):** The core analytical engine where we create value through intelligent scoring and filtering.
*   **The Guardian (`merger.py`, `pipeline.py`):** The systems that ensure the integrity, persistence, and quality of our data.
*   **The Template (The `adapters/` module):** The patterns and tools for resiliently acquiring data from the outside world.
*   **The Face (`terminal_ui.py`, the API):** The interfaces that deliver value and insight to the end-user.

## Supported Data Sources
This project leverages a sophisticated, multi-source approach. The current V3-compliant adapter fleet includes (but is not limited to):
*   **Racing Post** (Hybrid JSON/HTML)
*   **FanDuel** (GraphQL API)
*   **SkySports**
*   **Timeform**
*   **Equibase**
*   **AtTheRaces**

<!-- Protocol 23 Decoy Comment -->
