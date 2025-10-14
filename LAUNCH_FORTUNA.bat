@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION
TITLE Fortuna Faucet - Launcher v3.0

REM --- Phase 0: Setup Logging ---
IF NOT EXIST logs mkdir logs
SET "TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
SET "TIMESTAMP=%TIMESTAMP: =0%"
SET "BACKEND_LOG=logs\backend_%TIMESTAMP%.log"
SET "FRONTEND_LOG=logs\frontend_%TIMESTAMP%.log"

cls
ECHO.
ECHO     ================================================
ECHO       FORTUNA FAUCET - INTELLIGENT LAUNCHER v3.0
ECHO     ================================================
ECHO.
ECHO     See %BACKEND_LOG% and %FRONTEND_LOG% for detailed output.
ECHO.

REM --- Phase 1: Port Availability Check ---
ECHO [....] 1/4 Port Availability Check...
SET "BACKEND_PORT=8000"
SET "FRONTEND_PORT=3000"
SET "PORTS_CLEARED=true"
FOR %%P IN (%BACKEND_PORT% %FRONTEND_PORT%) DO (
    netstat -ano | findstr ":%%P" | findstr "LISTENING" >nul
    IF !ERRORLEVEL! EQU 0 (
        FOR /f "tokens=5" %%a IN ('netstat -ano ^| findstr ":%%P" ^| findstr "LISTENING"') DO ( taskkill /F /PID %%a >nul 2>&1 )
    )
)
ECHO [ OK ] 1/4 Port Availability Check - Complete.

REM --- Phase 2: Launch Backend Service ---
ECHO [....] 2/4 Launching Backend Service...
start "Fortuna Backend" /B cmd /c "call .venv\Scripts\activate.bat && uvicorn python_service.api:app --host 127.0.0.1 --port %BACKEND_PORT% --log-level warning > %BACKEND_LOG% 2>&1"
ECHO [ OK ] 2/4 Launching Backend Service - Process started.

REM --- Phase 3: Wait for Backend Health ---
ECHO [....] 3/4 Waiting for Backend to become healthy...
SET /a ATTEMPTS=0
:BackendHealthCheck
SET /a ATTEMPTS+=1
IF %ATTEMPTS% GTR 30 ( ECHO [FAIL] 3/4 Backend failed to start. Check %BACKEND_LOG%. && PAUSE && EXIT /B 1 )
powershell -Command "(Invoke-WebRequest -Uri http://localhost:%BACKEND_PORT%/health -UseBasicParsing).StatusCode" 2>nul | findstr "200" >nul
IF !ERRORLEVEL! NEQ 0 ( timeout /t 1 /nobreak >nul && GOTO BackendHealthCheck )
ECHO [ OK ] 3/4 Waiting for Backend to become healthy - Success!

REM --- Phase 4: Launch Frontend and Browser ---
ECHO [....] 4/4 Launching Frontend and Browser...
start "Fortuna Frontend" /B cmd /c "cd web_platform\frontend && npm run dev > %FRONTEND_LOG% 2>&1"
timeout /t 8 /nobreak >nul
start http://localhost:%FRONTEND_PORT%
ECHO [ OK ] 4/4 Launching Frontend and Browser - Complete.
ECHO.
ECHO  ================================================
ECHO   LAUNCH COMPLETE! THE FAUCET IS FLOWING.
ECHO  ================================================
ECHO.
ECHO   Press any key to launch the continuous status console...
PAUSE >NUL

REM Activate venv and run the status CLI
call .venv\Scripts\activate.bat
python fortuna_status_cli.py
