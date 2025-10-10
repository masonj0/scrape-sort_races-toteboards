@echo off
REM ============================================================================
REM  Project Gemini: WHOLE-SYSTEM Windows Setup Script
REM ============================================================================

echo [INFO] Starting full-stack setup for Project Gemini...

REM --- Section 1: Python Backend Setup ---
echo.
echo [BACKEND] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found. Please install Python 3.8+ and add to PATH.
    goto :eof
)
echo [BACKEND] Python found.

echo [BACKEND] Creating Python virtual environment in '.\\.venv\\'...
if not exist .\\.venv ( python -m venv .venv )

echo [BACKEND] Installing dependencies from 'python_service/requirements.txt'...
call .\\.venv\\Scripts\\activate.bat && pip install -r python_service/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Backend setup failed.
    goto :eof
)
echo [SUCCESS] Python backend setup complete.

REM --- Section 2: TypeScript Frontend Setup ---
echo.
echo [FRONTEND] Checking for Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found. Please install Node.js (LTS).
    goto :eof
)
echo [FRONTEND] Node.js found.

echo [FRONTEND] Installing dependencies from 'package.json'...
cd web_platform/frontend
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend setup failed. Check npm errors.
    cd ../..
    goto :eof
)

echo [FRONTEND] Checking for frontend environment file...
if not exist .env.local (
    echo [FRONTEND] '.env.local' not found. Creating from template...
    copy .env.local.example .env.local
    echo.
    echo    ****************************************************************************
    echo    *  [ACTION REQUIRED] Please edit 'web_platform/frontend/.env.local'      *
    echo    *  and add your NEXT_PUBLIC_API_KEY for the frontend to work.            *
    echo    ****************************************************************************
    echo.
) else (
    echo [FRONTEND] '.env.local' already exists.
)

cd ../..
echo [SUCCESS] TypeScript frontend setup complete.

REM --- Final Instructions ---
echo.
echo ============================================================================
REM  FULL-STACK SETUP COMPLETE!
REM  You can now launch the entire application with 'run_fortuna.bat'
REM ============================================================================

:eof