# Checkmate V8: The Quad-Hybrid Racing Analysis Platform

This repository contains the complete source code for Checkmate V8, a professional-grade, multi-language horse racing analysis platform.

---

## 🏛️ Project Architecture

The project is a **Penta-Hybrid** system designed for performance and flexibility:

*   **🐍 Python Service:** Handles data collection and orchestration.
*   **🦀 Rust Engine:** High-performance computational analysis.
*   **🖥️ C# Desktop App:** A native Windows "Command Deck" for power users.
*   **🌐 TypeScript Web Platform:** A modern, real-time "Live Cockpit."
*   **📊 Excel VBA Frontend:** A familiar interface for analysis and manual data stewardship.

All components are decoupled via a shared **SQLite database**.

---
## 🚀 Quick Start (Python Service)

**Running the Service:**
The primary entry point for the Python service is `python_service/main.py`. From the project root, run:
```bash
python -m python_service.main
```

**Building the Executable:**
A build script is provided to create a standalone Windows executable of the Python service.
```bash
python build_python_service.py
```
The output will be located in the `dist/` directory.