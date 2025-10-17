@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Stop Script (Graceful Shutdown)
REM ============================================================================

echo.
echo  [*] Stopping Fortuna Faucet services...
echo.

REM --- Stop Backend (Python) ---
echo  [BACKEND] Terminating Python processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Fortuna Backend" >nul 2>&1

REM --- Stop Frontend (Node) ---
echo  [FRONTEND] Terminating Node.js processes...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Fortuna Frontend" >nul 2>&1

REM --- Stop Watchman (Optional) ---
echo  [WATCHMAN] Terminating autonomous agent...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Fortuna Watchman" >nul 2>&1

echo.
echo  [*] Waiting for ports to be released...
timeout /t 2 /nobreak >nul

echo  [OK] All services stopped
echo.