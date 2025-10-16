@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Service Manager v2.0 (Single Entry Point)
REM ============================================================================

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

:menu
cls
echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Service Manager
echo  ========================================================================
echo.
echo   [1] Start Services (Full Launch)
echo   [2] Stop Services
echo   [3] Restart Services
echo   [4] Check Live Status
echo   [5] View Latest Logs
echo   [6] Exit
echo.
echo  ========================================================================
echo.

choice /C 123456 /N /M "Select an option: "

if errorlevel 6 goto :EOF
if errorlevel 5 goto logs
if errorlevel 4 goto status
if errorlevel 3 goto restart
if errorlevel 2 goto stop
if errorlevel 1 goto start

:start
call "%~dp0LAUNCH_FORTUNA.bat"
pause
goto menu

:stop
call "%~dp0STOP_FORTUNA.bat"
pause
goto menu

:restart
call "%~dp0RESTART_FORTUNA.bat"
pause
goto menu

:status
cls
echo.
echo  [*] Checking live service status...
echo.
echo  Backend Status:
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing; if ($r.StatusCode -eq 200) { Write-Host '[OK] Online' -ForegroundColor Green } else { Write-Host '[FAIL] Unexpected Status' -ForegroundColor Red } } catch { Write-Host '[FAIL] OFFLINE' -ForegroundColor Red }"

echo.
echo  Frontend Status:
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing; if ($r.StatusCode -eq 200) { Write-Host '[OK] Online' -ForegroundColor Green } else { Write-Host '[FAIL] Unexpected Status' -ForegroundColor Red } } catch { Write-Host '[FAIL] OFFLINE' -ForegroundColor Red }"

echo.
pause
goto menu

:logs
cls
echo.
echo  [*] Searching for the latest log files...
echo.

set "LATEST_BACKEND_LOG="
for /f "delims=" %%i in ('dir /b /o-d logs\\backend_*.log') do (
    set "LATEST_BACKEND_LOG=%%i"
    goto :found_backend
)
:found_backend
if defined LATEST_BACKEND_LOG (
    echo  [OK] Opening latest backend log: %LATEST_BACKEND_LOG%
    start notepad "logs\%LATEST_BACKEND_LOG%"
) else (
    echo  [FAIL] No backend log files found in the 'logs' directory.
)

set "LATEST_FRONTEND_LOG="
for /f "delims=" %%i in ('dir /b /o-d logs\\frontend_*.log') do (
    set "LATEST_FRONTEND_LOG=%%i"
    goto :found_frontend
)
:found_frontend
if defined LATEST_FRONTEND_LOG (
    echo  [OK] Opening latest frontend log: %LATEST_FRONTEND_LOG%
    start notepad "logs\%LATEST_FRONTEND_LOG%"
) else (
    echo  [FAIL] No frontend log files found in the 'logs' directory.
)

echo.
pause
goto menu