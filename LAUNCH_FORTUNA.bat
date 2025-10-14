@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION
TITLE Fortuna Faucet - Launcher v4.0

REM ============================================================================
REM  FORTUNA FAUCET - Intelligent Launcher v4.0
REM  Includes: Pre-flight checks for .env, running processes, and ports.
REM ============================================================================

cls
ECHO.
ECHO     ================================================
ECHO       FORTUNA FAUCET - INTELLIGENT LAUNCHER v4.0
ECHO     ================================================
ECHO.

REM --- Phase 1: Pre-Flight Validation ---
ECHO [....] 1/5 Pre-Flight Validation: Checking for .env file...
IF NOT EXIST .env (
    ECHO [WARN] CRITICAL: .env file not found!
    ECHO [INFO] Running setup wizard to create one...
    ECHO.
    call .venv\Scripts\activate.bat
    python setup_wizard.py
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [FAIL] Setup wizard failed or was cancelled. Aborting launch.
        PAUSE
        EXIT /B 1
    )
    ECHO [ OK ] .env file created successfully.
) ELSE (
    ECHO [ OK ] .env file found.
)

ECHO [....] 2/5 Pre-Flight Validation: Checking for existing processes...
tasklist /FI "WINDOWTITLE eq Fortuna Backend*" 2>NUL | find /I /N "cmd.exe">NUL
IF "%ERRORLEVEL%"=="0" (
    ECHO [WARN] An existing 'Fortuna Backend' process was found.
    CHOICE /C YN /N /M "Stop the existing process and restart? (Y/N): "
    IF ERRORLEVEL 2 GOTO :eof
    CALL STOP_FORTUNA.bat
    timeout /t 2 /nobreak >nul
)
ECHO [ OK ] No running processes detected.

REM --- Phase 2: Port Availability Check ---
ECHO [....] 3/5 Port Availability Check...
SET "BACKEND_PORT=8000"
SET "FRONTEND_PORT=3000"
FOR %%P IN (%BACKEND_PORT% %FRONTEND_PORT%) DO (
    netstat -ano | findstr ":%%P" | findstr "LISTENING" >nul
    IF !ERRORLEVEL! EQU 0 (
        FOR /f "tokens=5" %%a IN ('netstat -ano ^| findstr ":%%P" ^| findstr "LISTENING"') DO ( taskkill /F /PID %%a >nul 2>&1 )
    )
)
ECHO [ OK ] 3/5 Port Availability Check - Complete.

REM --- Phase 3: Launch Backend Service ---
ECHO [....] 4/5 Launching Backend Service (minimized)...
SET "TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
SET "TIMESTAMP=%TIMESTAMP: =0%"
IF NOT EXIST logs mkdir logs
SET "BACKEND_LOG=logs\backend_%TIMESTAMP%.log"
start "Fortuna Backend" /MIN cmd /c "call .venv\Scripts\activate.bat && uvicorn python_service.api:app --host 127.0.0.1 --port %BACKEND_PORT% --log-level warning > %BACKEND_LOG% 2>&1"
ECHO [ OK ] 4/5 Launching Backend Service - Process started.

REM --- Phase 4: Wait for Backend Health ---
ECHO [....] 5/5 Waiting for Backend to become healthy...
SET /a ATTEMPTS=0
:BackendHealthCheck
SET /a ATTEMPTS+=1
IF %ATTEMPTS% GTR 30 ( ECHO [FAIL] 5/5 Backend failed to start. Check %BACKEND_LOG%. && PAUSE && EXIT /B 1 )
powershell -Command "(Invoke-WebRequest -Uri http://localhost:%BACKEND_PORT%/health -UseBasicParsing).StatusCode" 2>nul | findstr "200" >nul
IF !ERRORLEVEL! NEQ 0 ( timeout /t 1 /nobreak >nul && GOTO BackendHealthCheck )
ECHO [ OK ] 5/5 Waiting for Backend to become healthy - Success!

REM --- Phase 5: Launch Frontend and Browser ---
ECHO [INFO] Launching Frontend and Browser (minimized)...
SET "FRONTEND_LOG=logs\frontend_%TIMESTAMP%.log"
start "Fortuna Frontend" /MIN cmd /c "cd web_platform\frontend && npm run dev > ..\..\%FRONTEND_LOG% 2>&1"
timeout /t 8 /nobreak >nul
start http://localhost:%FRONTEND_PORT%
ECHO [ OK ] Frontend and Browser launched.
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
