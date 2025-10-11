@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Clean Restart Script
REM ============================================================================

echo [%date% %time%] Restarting Fortuna Faucet... >> fortuna_restart.log

call STOP_FORTUNA.bat
timeout /t 10 /nobreak >nul
call LAUNCH_FORTUNA.bat

echo [%date% %time%] Restart complete. >> fortuna_restart.log
