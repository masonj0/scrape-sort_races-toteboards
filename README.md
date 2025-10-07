# Fortuna Faucet

This repository contains the Fortuna Faucet project, a global, multi-source horse racing analysis tool. The project is a two-pillar system: a powerful, asynchronous Python backend that performs all data gathering, and a feature-rich TypeScript frontend.

---

## 🚀 Quick Start

### 1. Configure Your Environment

Run the setup script to ensure Python and Node.js are correctly configured and all dependencies are installed.

```batch
# From the project root:
setup_windows.bat
```

### 2. Launch the Application

Run the master launch script. This will start both the Python backend and the TypeScript frontend servers in parallel.

```batch
# From the project root:
run_fortuna.bat
```

The backend API will be available at `http://localhost:8000`.
The frontend will be available at `http://localhost:3000`.

### 4. Using the API

To use the API directly (e.g., with `curl` or other tools), you must provide the `API_KEY` set in your `.env` file via the `X-API-Key` header. This is required for all endpoints except `/health`.

```bash
# Example: Test the qualified races endpoint
curl -H "X-API-Key: YOUR_SECRET_API_KEY_HERE" http://localhost:8000/api/races/qualified/trifecta
```
