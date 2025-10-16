@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Service Manager v3.0 (Optimized & Feature-Rich)
REM ============================================================================
setlocal enabledelayedexpansion

REM --- Color Output Support ---
for /F "tokens=1,2 delims=#" %%a in ('prompt #$H# ^& for %%b in (1) do rem') do (
  set "BS=%%a"
)

REM --- Pre-Flight Check: Has setup been run? ---
IF NOT EXIST .venv\Scripts\activate.bat (
    cls
    echo.
    echo  ========================================================================
    echo   Welcome to Fortuna Faucet!
    echo  ========================================================================
    echo.
    echo   [INFO] First-time setup required.
    echo   The automated installation wizard will now run.
    echo.
    pause
    call "%~dp0INSTALL_FORTUNA.bat"
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo [FATAL] Setup failed. Please review the errors and try again.
        pause
        exit /b 1
    )
)

REM --- Create logs directory if missing ---
if not exist logs mkdir logs

:menu
cls
echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Service Manager v3.0
echo  ========================================================================
echo.
echo   Quick Actions:
echo   [1] Start Services (Full Launch)
echo   [2] Stop Services (Clean Shutdown)
echo   [3] Restart Services (Graceful)
echo   [4] Check Live Status
echo.
echo   Monitoring & Diagnostics:
echo   [5] View Latest Logs
echo   [6] View Performance Stats
echo   [7] Validate Dependencies
echo.
echo   System:
echo   [8] Rebuild Database Cache
echo   [9] Reset to Factory Settings
echo   [0] Exit
echo.
echo  ========================================================================
echo.

choice /C 1234567890 /N /M "Select an option: "

if errorlevel 10 goto :EOF
if errorlevel 9 goto factory_reset
if errorlevel 8 goto rebuild_cache
if errorlevel 7 goto validate_deps
if errorlevel 6 goto perf_stats
if errorlevel 5 goto logs
if errorlevel 4 goto status
if errorlevel 3 goto restart
if errorlevel 2 goto stop
if errorlevel 1 goto start

:start
cls
echo.
echo [*] Starting Fortuna Faucet services...
call "%~dp0LAUNCH_FORTUNA.bat"
echo.
pause
goto menu

:stop
cls
echo.
echo [*] Stopping Fortuna Faucet services (clean shutdown)...
call "%~dp0STOP_FORTUNA.bat"
echo.
pause
goto menu

:restart
cls
echo.
echo [*] Restarting Fortuna Faucet services...
call "%~dp0RESTART_FORTUNA.bat"
echo.
pause
goto menu

:status
cls
echo.
echo  ========================================================================
echo   LIVE SERVICE STATUS
echo  ========================================================================
echo.

REM --- Backend Health Check ---
echo  Checking Backend (http://localhost:8000/health)...
powershell -NoProfile -Command "^
try {^
    $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop;^
    if ($response.StatusCode -eq 200) {^
        $data = $response.Content | ConvertFrom-Json;^
        Write-Host '[OK] Backend is ONLINE' -ForegroundColor Green;^
        Write-Host ('    Status: ' + $data.status) -ForegroundColor Green;^
    }^
} catch {^
    Write-Host '[FAIL] Backend is OFFLINE' -ForegroundColor Red;^
}^
"

echo.

REM --- Frontend Health Check ---
echo  Checking Frontend (http://localhost:3000)...
powershell -NoProfile -Command "^
try {^
    $response = Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop;^
    if ($response.StatusCode -eq 200) {^
        Write-Host '[OK] Frontend is ONLINE' -ForegroundColor Green;^
    }^
} catch {^
    Write-Host '[FAIL] Frontend is OFFLINE' -ForegroundColor Red;^
}^
"

echo.

REM --- Port Check ---
echo  Active Connections:
netstat -ano | find "8000" >nul && echo   [OK] Port 8000 (Backend) is listening
netstat -ano | find "3000" >nul && echo   [OK] Port 3000 (Frontend) is listening

echo.
pause
goto menu

:logs
cls
echo.
echo  ========================================================================
echo   LATEST LOG FILES
echo  ========================================================================
echo.

set "LATEST_BACKEND_LOG="
for /f "delims=" %%i in ('dir /b /o-d logs\backend_*.log 2^>nul') do (
    set "LATEST_BACKEND_LOG=%%i"
    goto :found_backend
)

:found_backend
if defined LATEST_BACKEND_LOG (
    echo  [OK] Latest Backend Log: %LATEST_BACKEND_LOG%
    echo  Opening in Notepad...
    start notepad "logs\%LATEST_BACKEND_LOG%"
) else (
    echo  [INFO] No backend logs found yet. Start services first.
)

echo.

set "LATEST_FRONTEND_LOG="
for /f "delims=" %%i in ('dir /b /o-d logs\frontend_*.log 2^>nul') do (
    set "LATEST_FRONTEND_LOG=%%i"
    goto :found_frontend
)

:found_frontend
if defined LATEST_FRONTEND_LOG (
    echo  [OK] Latest Frontend Log: %LATEST_FRONTEND_LOG%
    echo  Opening in Notepad...
    start notepad "logs\%LATEST_FRONTEND_LOG%"
) else (
    echo  [INFO] No frontend logs found yet. Start services first.
)

echo.
pause
goto menu

:perf_stats
cls
echo.
echo  ========================================================================
echo   PERFORMANCE STATISTICS
echo  ========================================================================
echo.

echo  System Resources:
wmic os get totalvisiblememorsize,freephysicalmemory | find /v "TotalVisibleMemorySize"

echo.
echo  Python Process Memory:
tasklist /fi "imagename eq python.exe" /fo list /v 2>nul | find "Mem Usage" || echo   [INFO] No Python processes running

echo.
echo  Node.js Process Memory:
tasklist /fi "imagename eq node.exe" /fo list /v 2>nul | find "Mem Usage" || echo   [INFO] No Node processes running

echo.
echo  Disk Space (Project Directory):
dir /s "." 2>nul | find "File(s)" || echo   [INFO] Could not calculate size

echo.
pause
goto menu

:validate_deps
cls
echo.
echo  ========================================================================
echo   VALIDATING DEPENDENCIES
echo  ========================================================================
echo.

echo  [*] Checking Python...
python --version >nul 2>&1 && echo   [OK] Python is installed || echo   [FAIL] Python not found

echo  [*] Checking Python venv...
if exist .venv\Scripts\activate.bat (
    echo   [OK] Virtual environment exists
) else (
    echo   [FAIL] Virtual environment missing
)

echo  [*] Checking Node.js...
node --version >nul 2>&1 && echo   [OK] Node.js is installed || echo   [FAIL] Node.js not found

echo  [*] Checking npm...
npm --version >nul 2>&1 && echo   [OK] npm is installed || echo   [FAIL] npm not found

echo  [*] Checking git...
git --version >nul 2>&1 && echo   [OK] Git is installed || echo   [FAIL] Git not found

echo  [*] Checking curl...
curl --version >nul 2>&1 && echo   [OK] curl is installed || echo   [FAIL] curl not found (health checks disabled)

echo.
pause
goto menu

:rebuild_cache
cls
echo.
echo  [*] Rebuilding database cache...
call .venv\Scripts\activate.bat
cd python_service
python -m pytest --cache-clear 2>nul
cd ..
echo  [OK] Cache rebuild complete
echo.
pause
goto menu

:factory_reset
cls
echo.
echo  ========================================================================
echo   FACTORY RESET WARNING
echo  ========================================================================
echo.
echo  This will:
echo   - Delete all logs
echo   - Clear cache
echo   - Reset environment files
echo.
choice /C YN /N /M "Are you SURE? (Y/N): "
if errorlevel 2 goto menu
if errorlevel 1 (
    echo.
    echo  [*] Performing factory reset...
    if exist logs rmdir /s /q logs
    mkdir logs
    if exist .pytest_cache rmdir /s /q .pytest_cache
    if exist python_service\.pytest_cache rmdir /s /q python_service\.pytest_cache
    echo  [OK] Factory reset complete
)
echo.
pause
goto menu