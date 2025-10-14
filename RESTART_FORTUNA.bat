@ECHO OFF
TITLE Fortuna Faucet - Restart Script
ECHO.
ECHO  ========================================================================
ECHO   Fortuna Faucet - Restart Script
ECHO  ========================================================================
ECHO.
ECHO [INFO] Attempting to restart all Fortuna Faucet services...
ECHO.

CALL STOP_FORTUNA.bat

ECHO.
ECHO [INFO] All services stopped. Relaunching in 5 seconds...
ECHO.
timeout /t 5

CALL LAUNCH_FORTUNA.bat