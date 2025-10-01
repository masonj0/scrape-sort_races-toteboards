# Checkmate Ultimate Solo (Global Dominance Edition)

This repository contains the Checkmate Ultimate Solo project, a global, multi-source horse racing analysis tool. The project's final, perfected form is a two-pillar system: a powerful Python backend that performs all data gathering and analysis, serving a feature-rich TypeScript frontend.

---

## 🚀 Quick Start

### 1. Configure Your Environment

Run the setup script to ensure Python and Node.js are correctly configured and all dependencies are installed.

```batch
# From the project root:
setup_windows.bat
```

*Optional:* Edit the `.env` file to add your API key for the `RacingAndSports` adapter for Australian race data.

### 2. Run the Python Backend (Full Power)

```bash
# From the project root:
cd python_service
python api.py
```

### 3. Run the Ultimate TypeScript Frontend

```bash
# From the project root:
cd web_platform/frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000` in your browser.
