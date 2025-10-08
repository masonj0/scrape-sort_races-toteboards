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

REM --- Open Browser ---
echo [UI] Waiting 5 seconds for the frontend server to initialize...
timeout /t 5 /nobreak >nul
echo [UI] Opening the Fortuna Faucet dashboard in your default browser...
start http://localhost:3000

echo [SUCCESS] Both pillars of Fortuna Faucet have been launched.

:eof