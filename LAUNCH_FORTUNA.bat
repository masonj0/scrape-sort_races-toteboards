@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  Fortuna Faucet: Enhanced Launcher v2.1 (Hardened)
REM ============================================================================

REM --- Pre-Flight Check: Is it already running? ---
tasklist /FI "WINDOWTITLE eq Fortuna Backend" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [ERROR] Fortuna Faucet services appear to be already running.
    echo [INFO]  Please use 'STOP_FORTUNA.bat' or the Service Manager to stop them before launching again.
    pause
    goto :eof
)

echo [INFO] Launching Fortuna Faucet application...

REM --- Configuration ---
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set MAX_STARTUP_WAIT=30

REM --- Pre-Flight Checks ---
echo.
echo [CHECK] Running pre-flight checks...

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo [INFO] Run INSTALL_FORTUNA.bat first
    pause
    goto :eof
)

REM --- Launch Backend ---
echo.
echo [BACKEND] Starting FastAPI server...
start "Fortuna Backend" /MIN cmd /c "call .venv\Scripts\activate.bat && cd python_service && uvicorn api:app --reload --port %BACKEND_PORT% 2>&1 | findstr /V /C:"Waiting for changes""

REM --- Smart Wait for Backend ---
echo [BACKEND] Waiting for backend to be ready...
set WAIT_COUNT=0
:wait_backend
timeout /t 1 /nobreak >nul
set /a WAIT_COUNT+=1

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:%BACKEND_PORT%/health' -Method GET -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend is ready!
    goto :backend_ready
)

if %WAIT_COUNT% lss %MAX_STARTUP_WAIT% goto :wait_backend
echo [WARNING] Backend startup timeout, continuing anyway...

:backend_ready

REM --- Launch Frontend ---
echo.
echo [FRONTEND] Starting Next.js development server...
start "Fortuna Frontend" /MIN cmd /c "cd web_platform\frontend && npm run dev"

REM --- Wait for Frontend ---
echo [FRONTEND] Waiting for frontend to be ready...
timeout /t 8 /nobreak >nul

REM --- Open Browser ---
echo.
echo [UI] Opening dashboard in browser...
start "" "http://localhost:%FRONTEND_PORT%"

echo.
echo ============================================================================
echo   LAUNCH COMPLETE!
echo ============================================================================
pause

:eof
endlocal