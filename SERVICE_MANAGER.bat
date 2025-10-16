@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Service Manager v3.1 (UX Enhanced)
REM ============================================================================
setlocal enabledelayedexpansion

REM --- Pre-Flight Check: Has setup been run? ---
IF NOT EXIST .venv\Scripts\activate.bat (
    cls & echo [INFO] First-time setup required. & pause & call "%~dp0INSTALL_FORTUNA.bat"
    IF %ERRORLEVEL% NEQ 0 ( echo [FATAL] Setup failed. & pause & exit /b 1 )
)

:menu
cls
echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Service Manager v3.1
echo  ========================================================================
echo.
echo   Quick Actions:
echo   [1] Start Services      [2] Stop Services       [3] Restart Services
echo.
echo   Diagnostics & Tools:
echo   [4] Check Live Status   [5] View Latest Logs    [6] Validate Dependencies
echo   [7] Auto-Fix Issues     [8] Performance Stats   [9] Factory Reset
echo.
echo   System:
echo   [0] Exit
echo  ========================================================================
echo.

choice /C 1234567890 /N /M "Select an option: "

if errorlevel 10 goto :EOF
if errorlevel 9 goto factory_reset
if errorlevel 8 goto perf_stats
if errorlevel 7 goto auto_fix
if errorlevel 6 goto validate_deps
if errorlevel 5 goto logs
if errorlevel 4 goto status
if errorlevel 3 goto restart
if errorlevel 2 goto stop
if errorlevel 1 goto start

:start
cls & echo [*] Starting Fortuna Faucet services... & call "%~dp0LAUNCH_FORTUNA.bat" & goto end_pause

:stop
cls & echo [*] Stopping Fortuna Faucet services... & call "%~dp0STOP_FORTUNA.bat" & goto end_pause

:restart
cls & echo [*] Restarting Fortuna Faucet services... & call "%~dp0RESTART_FORTUNA.bat" & goto end_pause

:status
cls & echo [*] Checking Live Status... & call "%~dp0health_check.bat" & goto end_pause

:logs
cls & echo [*] Opening latest log files... & start notepad "logs\%COMPUTERNAME%_backend.log" & start notepad "logs\%COMPUTERNAME%_frontend.log" & goto end_pause

:validate_deps
cls & echo [*] Validating Dependencies... & call "%~dp0health_check.bat" & goto end_pause

:auto_fix
cls & echo [*] Launching Auto-Fix Utility... & call "%~dp0fix_common_issues.bat" & goto menu

:perf_stats
cls
echo  System Resources:
wmic os get totalvisiblememorysize,freephysicalmemory | find /v "TotalVisibleMemorySize"
echo.
echo  Python Process Memory:
tasklist /fi "imagename eq python.exe" /fo list /v 2>nul | find "Mem Usage" || echo   [INFO] No Python processes running
echo.
echo  Node.js Process Memory:
tasklist /fi "imagename eq node.exe" /fo list /v 2>nul | find "Mem Usage" || echo   [INFO] No Node processes running
goto end_pause

:factory_reset
cls
echo  [!!] FACTORY RESET WARNING [!!]
echo  This will delete all logs and caches.
choice /C YN /N /M "Are you SURE? (Y/N): "
if errorlevel 2 goto menu
if errorlevel 1 (
    echo  [*] Performing factory reset...
    if exist logs rmdir /s /q logs & mkdir logs
    if exist .pytest_cache rmdir /s /q .pytest_cache
    echo  [OK] Factory reset complete
)
goto end_pause

:end_pause
echo.
echo Press any key to return to the menu...
pause >nul
goto menu