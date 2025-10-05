@echo off
REM ============================================================================
REM  Project Gemini: Backend Launcher
REM ============================================================================

echo [INFO] Locating virtual environment...
if not exist .\\.venv\\Scripts\\activate.bat (
    echo [ERROR] Virtual environment not found. Please run 'setup_windows.bat' first.
    goto :eof
)

echo [INFO] Activating virtual environment...
call .\\.venv\\Scripts\\activate.bat

echo [INFO] Starting FastAPI server with uvicorn (hot-reloading enabled)...
uvicorn python_service.api:app --reload

:eof