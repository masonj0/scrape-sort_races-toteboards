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

### 2. Run the Python Backend (FastAPI)

```bash
# From the project root, activate the virtual environment:
venv\Scripts\activate

# Run the async server with Uvicorn:
cd python_service
uvicorn api:app --reload
```

### 3. Run the TypeScript Frontend

```bash
# From the project root:
cd web_platform/frontend
npm run dev
```