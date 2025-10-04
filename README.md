# Checkmate Ultimate Solo (V2 - FastAPI Edition)

This repository contains the Checkmate Ultimate Solo project, a global, multi-source horse racing analysis tool. The project is a two-pillar system: a powerful, asynchronous Python backend that performs all data gathering, and a feature-rich TypeScript frontend.

---

## 🚀 Quick Start

### 1. Configure Your Environment

Run the setup script to ensure Python and Node.js are correctly configured and all dependencies are installed.

```batch
# From the project root:
setup_windows.bat
```

Optional: Create a `.env` file in the project root and add your API keys (see `.env.example` when available).

### 2. Run the Python Backend (FastAPI)

```bash
# From the project root, activate the virtual environment:
venv\Scripts\activate

# Run the async server with Uvicorn:
cd python_service
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`.

### 3. Run the Ultimate TypeScript Frontend

```bash
# From the project root:
cd web_platform/frontend
npm run dev
```

Navigate to `http://localhost:3000` in your browser.