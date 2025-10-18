@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Windows Task Scheduler Setup (PowerShell Edition)
REM ============================================================================

title Fortuna Faucet - Task Scheduler Setup
color 0E

echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Automatic Startup Configuration
echo  ========================================================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Administrator privileges required!
    echo  [!] Right-click this script and select "Run as Administrator"
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0

echo  [1/2] Creating task to start Fortuna on Windows login (via PowerShell)...
REM UPGRADED: This now calls the superior launcher.ps1 script directly.
schtasks /create /tn "Fortuna Faucet - Startup" /tr "powershell.exe -ExecutionPolicy Bypass -File \"%SCRIPT_DIR%launcher.ps1\"" /sc onlogon /rl highest /f

echo  [2/2] Creating daily maintenance task...
schtasks /create /tn "Fortuna Faucet - Daily Restart" /tr "%SCRIPT_DIR%RESTART_FORTUNA.bat" /sc daily /st 03:00 /rl highest /f

echo.
echo  ========================================================================
echo   SCHEDULED TASKS CREATED SUCCESSFULLY!
echo  ========================================================================
echo.
echo   Fortuna will now start automatically when you log into Windows.
echo   It will also perform a clean restart every morning at 3:00 AM.
echo.
pause
