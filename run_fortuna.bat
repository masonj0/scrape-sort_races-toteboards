@echo off
REM ============================================================================
REM  Fortuna Faucet: Master Launcher (v2 - Perfected)
REM ============================================================================

echo [INFO] Launching the Fortuna Faucet application...

REM --- Launch Backend ---
echo [BACKEND] Starting FastAPI server... (New window)
start "Fortuna Backend" cmd /c "call .\\.venv\\Scripts\\activate.bat && cd python_service && uvicorn api:app --reload"

REM --- Launch Frontend ---
echo [FRONTEND] Starting Next.js development server... (New window)
start "Fortuna Frontend" cmd /c "cd web_platform/frontend && npm run dev"

REM --- Launch Pillar 3: The Autonomous Watchman (Optional) ---
echo [WATCHMAN] Starting autonomous agent... (New window)
start "Fortuna Watchman" cmd /c "call .\\.venv\\Scripts\\activate.bat && python python_service/fortuna_watchman.py"

REM --- Open Browser ---
echo [UI] Waiting 5 seconds for the frontend server to initialize...
timeout /t 5 /nobreak >nul
echo [UI] Opening the Fortuna Faucet dashboard in your default browser...
start http://localhost:3000

echo [SUCCESS] All three pillars of Fortuna Faucet have been launched.

:eof