# Checkmate V8: The Penta-Hybrid Racing Analysis Platform

This repository contains the complete source code for Checkmate V8, a professional-grade, multi-language horse racing analysis platform.

---

## 🏛️ Project Architecture

The project is a **Penta-Hybrid** system designed for performance, flexibility, and a rich user experience. Each component has a specialized role:

*   **🐍 Python Service:** The core data collection and analysis engine.
*   **🦀 Rust Engine:** High-performance computational analysis for the Python service.
*   **🖥️ C# Desktop App:** A native Windows "Command Deck" for power users.
*   **🌐 TypeScript Web Platform:** A modern, real-time "Live Cockpit."
*   **📊 Excel VBA Frontend:** A familiar interface for analysis and manual data stewardship.

All components are decoupled and communicate via a shared **SQLite database**.

---
## 🚀 Quick Start

There are two primary ways to run the system:

### 1. The Master Launcher (Recommended)

The `launcher.py` script orchestrates all components of the Penta-Hybrid system.

```bash
# From the project root:
python launcher.py
```

### 2. Standalone Tipsheet Generator

To run only the lightweight, integrated tipsheet generator:

```bash
# From the project root:
python tipsheet_generator.py
```

### Environment Setup

Before the first run, prepare your Windows environment by running the setup script:

```batch
setup_windows.bat
```