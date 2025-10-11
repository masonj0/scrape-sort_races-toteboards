@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Clean Shutdown Script
REM ============================================================================

title Fortuna Faucet - Shutdown
color 0C

echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Shutting Down All Services
echo  ========================================================================
echo.

echo  [*] Stopping Python processes...
taskkill /FI "WindowTitle eq Fortuna Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Fortuna Monitor*" /T /F >nul 2>&1

echo  [*] Stopping Node.js processes...
taskkill /FI "WindowTitle eq Fortuna Frontend*" /T /F >nul 2>&1

echo.
echo  [V] All Fortuna services stopped successfully!
echo.
pause
