@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Service Manager (One-Click Operations)
REM ============================================================================

:menu
cls
echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Service Manager
necho  ========================================================================
echo.
echo   [1] Start Services (Full Launch)
necho   [2] Stop Services
necho   [3] Restart Services
necho   [4] Check Live Status
necho   [5] View Latest Logs
necho   [6] Exit
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
echo.
echo  [*] Starting Fortuna Faucet services...
echo.
call "%~dp0LAUNCH_FORTUNA.bat"
pause
goto menu

:stop
echo.
echo  [*] Stopping Fortuna Faucet services...
echo.
call "%~dp0STOP_FORTUNA.bat"
pause
goto menu

:restart
echo.
echo  [*] Restarting Fortuna Faucet services...
echo.
call "%~dp0RESTART_FORTUNA.bat"
pause
goto menu

:status
echo.
echo  [*] Checking live service status...
echo.
echo  Backend Status:
REM Use PowerShell for a more reliable check
powershell -Command "try { (Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing).StatusCode } catch { 'OFFLINE' }" 2>nul

echo.
echo  Frontend Status:
powershell -Command "try { (Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing).StatusCode } catch { 'OFFLINE' }" 2>nul

echo.
pause
goto menu

:logs
echo.
echo  [*] Opening latest log files...

REM Find the most recent backend log
FOR /F "delims=" %%F IN ('dir /b /o-d logs\backend_*.log') DO (
    start notepad "logs\%%F"
    GOTO FoundFrontendLog
)

:FoundFrontendLog
REM Find the most recent frontend log
FOR /F "delims=" %%F IN ('dir /b /o-d logs\frontend_*.log') DO (
    start notepad "logs\%%F"
    GOTO EndLogs
)

:EndLogs
pause
goto menu