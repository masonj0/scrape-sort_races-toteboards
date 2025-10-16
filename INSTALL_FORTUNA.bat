@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Installation Wizard (Optimized)
REM ============================================================================
setlocal enabledelayedexpansion

cls
echo.
echo  ========================================================================
echo   Fortuna Faucet - First-Time Installation
echo  ========================================================================
echo.

REM --- Check Python ---
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [FAIL] Python 3.8+ is required but not found
    echo  Download from: https://python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo  [OK] Python %PYTHON_VER% found

REM --- Check Node.js ---
echo.
echo  [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [FAIL] Node.js LTS is required but not found
    echo  Download from: https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo  [OK] Node.js %NODE_VER% found

REM --- Create Python venv ---
echo.
echo  [3/5] Creating Python virtual environment...
if not exist .venv (
    python -m venv .venv --without-pip
    echo  [*] Installing pip and setuptools...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel --quiet >nul 2>&1
)
call .venv\Scripts\activate.bat
echo  [OK] Virtual environment ready

REM --- Install Python dependencies ---
echo.
echo  [4/5] Installing Python dependencies (this may take 2-3 minutes)...
pip install -r python_service/requirements.txt --quiet --use-deprecated=legacy-resolver >nul 2>&1
if %errorlevel% neq 0 (
    echo  [FAIL] Python dependency installation failed
    pause
    exit /b 1
)
echo  [OK] Python dependencies installed

REM --- Install Node dependencies ---
echo.
echo  [5/5] Installing Node.js dependencies (this may take 1-2 minutes)...
cd web_platform\frontend
call npm ci --prefer-offline --no-audit --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo  [FAIL] Node dependency installation failed
    cd ..\..
    pause
    exit /b 1
)

if not exist .env.local (
    copy .env.local.example .env.local >nul 2>&1
)
cd ..\..
echo  [OK] Node dependencies installed

REM --- Create logs directory ---
if not exist logs mkdir logs

echo.
echo  ========================================================================
echo   Installation Complete!
echo  ========================================================================
echo.
echo  Next steps:
echo   1. Edit .env file with your API credentials
echo   2. Run SERVICE_MANAGER.bat
echo   3. Select option [1] to start services
echo.
pause
exit /b 0