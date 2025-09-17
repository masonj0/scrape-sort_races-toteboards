@echo off
setlocal

echo =================================================
echo  Checkmate V7 Windows Setup
echo =================================================
echo.

REM Check for Python
echo Checking for Python 3.10+...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10 or higher and ensure it's added to your PATH.
    goto :eof
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%
echo.

REM Check if venv already exists
if exist venv (
    echo Virtual environment 'venv' already exists. Skipping creation.
) else (
    echo Creating Python virtual environment in '.\venv\'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        goto :eof
    )
    echo Virtual environment created successfully.
)
echo.

REM Activate venv and install requirements
echo Activating virtual environment and installing dependencies from requirements.txt...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Please check requirements.txt and your internet connection.
    goto :eof
)
echo.

echo =================================================
echo  Setup Complete!
echo =================================================
echo You can now run 'launch_checkmate.bat' to start the application.
echo.

endlocal
pause
