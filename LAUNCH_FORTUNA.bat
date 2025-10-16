@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Launch Script (v3 - Race-Condition Free)
REM ============================================================================
setlocal enabledelayedexpansion

set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set MAX_WAIT=60
set HEALTH_INTERVAL=1

echo.
echo  [*] Starting Fortuna Faucet services...
echo.

REM --- Start Backend ---
echo  [BACKEND] Launching on port %BACKEND_PORT%...
start "Fortuna Backend" cmd /k ^
  "call .venv\Scripts\activate.bat && ^
   cd python_service && ^
   uvicorn api:app --host 127.0.0.1 --port 8000 >> ..\logs\backend_!date:~-4!-!date:~-10,2!-!date:~-7,2!_!time:~0,2!-!time:~3,2!-!time:~6,2!.log 2>&1"

REM --- Wait for Backend to be ready ---
set /a WAIT=0
:wait_backend
timeout /t %HEALTH_INTERVAL% /nobreak >nul
powershell -NoProfile -Command "^
try {^
    Invoke-WebRequest -Uri 'http://localhost:%BACKEND_PORT%/health' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop ^| Out-Null;^
    exit 0^
} catch {^
    exit 1^
}^
" >nul 2>&1

if %errorlevel% equ 0 (
    echo  [OK] Backend is ready
    goto launch_frontend
)

set /a WAIT+=HEALTH_INTERVAL
if !WAIT! geq %MAX_WAIT% (
    echo  [FAIL] Backend failed to start after %MAX_WAIT% seconds
    echo  Check logs\backend_*.log for details
    pause
    exit /b 1
)
goto wait_backend

REM --- Start Frontend ---
:launch_frontend
echo.
echo  [FRONTEND] Launching on port %FRONTEND_PORT%...
start "Fortuna Frontend" cmd /k ^
  "cd web_platform\frontend && ^
   npm run dev >> ..\..\logs\frontend_!date:~-4!-!date:~-10,2!-!date:~-7,2!_!time:~0,2!-!time:~3,2!-!time:~6,2!.log 2>&1"

REM --- Wait for Frontend to be ready ---
set /a WAIT=0
:wait_frontend
timeout /t %HEALTH_INTERVAL% /nobreak >nul
powershell -NoProfile -Command "^
try {^
    Invoke-WebRequest -Uri 'http://localhost:%FRONTEND_PORT%' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop ^| Out-Null;^
    exit 0^
} catch {^
    exit 1^
}^
" >nul 2>&1

if %errorlevel% equ 0 (
    echo  [OK] Frontend is ready
    goto open_dashboard
)

set /a WAIT+=HEALTH_INTERVAL
if !WAIT! geq %MAX_WAIT% (
    echo  [FAIL] Frontend failed to start after %MAX_WAIT% seconds
    echo  Check logs\frontend_*.log for details
    pause
    exit /b 1
)
goto wait_frontend

:open_dashboard
echo.
echo  [*] Opening dashboard in browser...
timeout /t 2 /nobreak >nul
start http://localhost:%FRONTEND_PORT%

echo.
echo  ========================================================================
echo   All Services Running!
echo  ========================================================================
echo.
echo   Backend:  http://localhost:%BACKEND_PORT%/docs
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo   Logs:     logs\backend_*.log and logs\frontend_*.log
echo.
echo  To stop services, run SERVICE_MANAGER.bat and select option [2]
echo.