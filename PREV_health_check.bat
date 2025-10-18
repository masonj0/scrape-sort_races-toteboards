@echo off
REM ============================================================================
REM  Fortuna Faucet: System Health Check
REM ============================================================================

echo ========================================
echo   Fortuna Faucet - System Health Check
echo ========================================
echo.

REM --- Check Python ---
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found
    python --version
) else (
    echo [FAIL] Python not found
)
echo.

REM --- Check Node.js ---
echo [2/7] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js found
    node --version
) else (
    echo [FAIL] Node.js not found
)
echo.

REM --- Check Virtual Environment ---
echo [3/7] Checking Python virtual environment...
if exist .venv (
    echo [OK] Virtual environment exists
    call .venv\Scripts\activate.bat
    python -c "import sys; print(f'Python location: {sys.executable}')"
) else (
    echo [FAIL] Virtual environment not found
)
echo.

REM --- Check Configuration ---
echo [4/7] Checking configuration files...
if exist .env (
    echo [OK] .env file found
) else (
    echo [WARN] .env file not found
)

if exist web_platform\frontend\.env.local (
    echo [OK] Frontend .env.local found
) else (
    echo [WARN] Frontend .env.local not found
)
echo.

REM --- Check Backend Dependencies ---
echo [5/7] Checking backend dependencies...
call .venv\Scripts\activate.bat
pip check >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] All dependencies satisfied
) else (
    echo [WARN] Dependency conflicts detected
    pip check
)
echo.

REM --- Check Frontend Dependencies ---
echo [6/7] Checking frontend dependencies...
cd web_platform\frontend
if exist node_modules (
    echo [OK] Frontend dependencies installed
) else (
    echo [FAIL] Frontend dependencies not installed
)
cd ..\..
echo.

REM --- Check Ports ---
echo [7/7] Checking port availability...
netstat -ano | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo [WARN] Port 8000 is in use
) else (
    echo [OK] Port 8000 available
)

netstat -ano | findstr ":3000" >nul
if %errorlevel% equ 0 (
    echo [WARN] Port 3000 is in use
) else (
    echo [OK] Port 3000 available
)
echo.

echo ========================================
echo   Health Check Complete
echo ========================================
pause