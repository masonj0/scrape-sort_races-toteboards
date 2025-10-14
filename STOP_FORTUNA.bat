@ECHO OFF
TITLE Fortuna Faucet - Shutdown Script
ECHO.
ECHO  ========================================================================
ECHO   Fortuna Faucet - Shutdown Script
ECHO  ========================================================================
ECHO.
ECHO [INFO] Attempting to gracefully shut down all Fortuna Faucet services...

REM Find and kill the backend uvicorn process specifically tied to our API
FOR /F "tokens=2" %%I IN ('wmic process where "commandline like '%%python_service.api:app%%'" get processid /format:list ^| find "="') DO (
    ECHO [OK] Found and stopping backend service (PID: %%I).
    taskkill /F /PID %%I >nul
)

REM Find and kill the frontend Next.js process
FOR /F "tokens=2" %%I IN ('wmic process where "commandline like '%%next dev%%' and caption='node.exe'" get processid /format:list ^| find "="') DO (
    ECHO [OK] Found and stopping frontend service (PID: %%I).
    taskkill /F /PID %%I >nul
)

ECHO.
ECHO [INFO] Shutdown complete.
PAUSE