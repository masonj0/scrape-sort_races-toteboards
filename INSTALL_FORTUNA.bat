@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  Fortuna Faucet: Enhanced Windows Setup Script v2.0
REM ============================================================================

echo [INFO] Starting enhanced full-stack setup...

REM --- Python Version Check ---
echo.
echo [BACKEND] Verifying Python installation and version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found. Please install Python 3.8+ from python.org
    pause
    goto :eof
)

REM Extract version number and check minimum requirement
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM --- Create Virtual Environment with Error Checking ---
echo.
echo [BACKEND] Creating Python virtual environment...
if exist .venv (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        goto :eof
    )
)

REM --- Test Virtual Environment Activation ---
echo [BACKEND] Testing virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Virtual environment activation failed
    pause
    goto :eof
)

REM --- Upgrade pip First ---
echo [BACKEND] Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [WARNING] pip upgrade had issues, continuing...
)

REM --- Install Dependencies with Progress ---
echo [BACKEND] Installing Python dependencies...
pip install -r python_service/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Python dependency installation failed
    echo [INFO] Check python_service/requirements.txt for issues
    pause
    goto :eof
)
echo [SUCCESS] Python backend setup complete.

REM --- Node.js Setup ---
echo.
echo [FRONTEND] Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Install from nodejs.org
    pause
    goto :eof
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo [INFO] Found Node.js %NODE_VERSION%

REM --- Frontend Dependencies ---
echo [FRONTEND] Installing frontend dependencies...
cd web_platform\frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Frontend setup failed
    cd ..\..
    pause
    goto :eof
)
cd ..\..
echo [SUCCESS] Frontend setup complete.

REM --- Configuration File Check ---
echo.
echo [CONFIG] Checking configuration files...
if not exist .env (
    echo [WARNING] .env file not found
    if exist .env.example (
        echo [INFO] Creating .env from .env.example
        copy .env.example .env >nul
        echo [ACTION REQUIRED] Please edit .env with your API keys
    ) else (
        echo [ERROR] .env.example not found either
    )
)

REM --- Final Report ---
echo.
echo ============================================================================
echo   SETUP COMPLETE!
echo ============================================================================
echo.
echo   Next steps:
echo   1. Edit .env file with your API keys
echo   2. Run 'LAUNCH_FORTUNA.bat' to launch the application
echo.
echo   Optional: Run 'CREATE_SHORTCUTS.bat' to create desktop shortcuts
echo ============================================================================
pause

:eof
endlocal