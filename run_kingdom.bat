@echo off
REM ============================================================================
REM  Project Gemini: One-Click Kingdom Launcher
REM ============================================================================

echo [INFO] Launching the Ultimate Solo application...

REM --- Launch Backend ---
echo [BACKEND] Starting FastAPI server... (New window)
start "Checkmate Backend" cmd /c "call .\\.venv\\Scripts\\activate.bat && cd python_service && uvicorn api:app --reload"

REM --- Launch Frontend ---
echo [FRONTEND] Starting Next.js development server... (New window)
start "Checkmate Frontend" cmd /c "cd web_platform/frontend && npm run dev"

echo [SUCCESS] Both pillars of the kingdom have been launched.

:eof