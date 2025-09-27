# Checkmate V8: Windows Hybrid Architecture

This project is a high-performance, single-user desktop application for real-time horse racing analysis. It uses a hybrid architecture to maximize performance and reliability.

## Architecture

- **Python Backend Service:** A silent Windows service responsible for all data collection, web scraping, and API integration. It writes clean, structured data to a local SQLite database.
- **C# Desktop Application:** A rich, native Windows desktop application for all analysis, display, and user interaction. It reads data from the SQLite database with near-zero latency, providing an instantaneous user experience.

## File Structure

```
/ (Repo Root)
├── python_service/         # The complete Python backend
│   ├── service.py
│   ├── engine.py
│   └── requirements.txt
└── README.md
```