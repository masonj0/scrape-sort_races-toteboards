@echo off
REM ============================================================================
REM  Project Gemini: Windows Setup Script
REM
REM  This script automates the setup of the Python backend environment.
REM  It will:
REM  1. Create a Python virtual environment in the '.venv' directory.
REM  2. Activate the virtual environment.
REM  3. Install all required dependencies from 'python_service/requirements.txt'.
REM ============================================================================

echo [INFO] Starting Project Gemini backend setup for Windows...

REM --- Check for Python ---
echo [INFO] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in the system's PATH.
    echo [ERROR] Please install Python 3.8+ and ensure it is added to your PATH.
    goto :eof
)
echo [SUCCESS] Python found.

REM --- Create Virtual Environment ---
echo [INFO] Creating Python virtual environment in '.\.venv\'...
if not exist .\.venv (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create the virtual environment.
        goto :eof
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment '.\.venv\' already exists. Skipping creation.
)

REM --- Activate and Install Dependencies ---
echo [INFO] Activating virtual environment and installing dependencies...
call .\.venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate the virtual environment.
    goto :eof
)

echo [INFO] Installing packages from 'python_service/requirements.txt'...
pip install -r python_service/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check 'requirements.txt' and your connection.
    goto :eof
)
echo [SUCCESS] All dependencies installed successfully.

REM --- Final Instructions ---
echo.
echo ============================================================================
echo  Setup Complete!
echo ============================================================================
echo.
echo  To activate the environment in your current command prompt, run:
echo.
echo      call .\.venv\Scripts\activate.bat
echo.
echo  The Python backend is now ready.
echo ============================================================================

:eof