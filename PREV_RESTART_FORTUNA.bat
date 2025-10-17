@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Restart Script (Graceful Restart)
REM ============================================================================

echo.
echo  [*] Restarting Fortuna Faucet services...
echo.

call "%~dp0STOP_FORTUNA.bat"

echo.
echo  [*] Waiting before restart...
timeout /t 3 /nobreak >nul

call "%~dp0LAUNCH_FORTUNA.bat"