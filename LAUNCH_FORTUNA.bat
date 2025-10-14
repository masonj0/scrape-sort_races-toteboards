@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION
TITLE Fortuna Ascended - Launcher v2.0

REM ============================================================================
REM  Fortuna Ascended - Intelligent Launch System v2.0
REM ============================================================================
ECHO.
ECHO  ========================================================================
ECHO   Fortuna Ascended - Intelligent Launcher
ECHO  ========================================================================
ECHO.

REM --- Phase 1: Port Availability Check ---
ECHO [1/4] Checking for available network ports...
SET "BACKEND_PORT=8000"
SET "FRONTEND_PORT=3000"
SET "PORTS_CLEARED=true"

FOR %%P IN (%BACKEND_PORT% %FRONTEND_PORT%) DO (
    netstat -ano | findstr ":%%P" | findstr "LISTENING" >nul
    IF !ERRORLEVEL! EQU 0 (
        ECHO [WARN] Port %%P is currently in use. Attempting to free it...
        FOR /f "tokens=5" %%a IN ('netstat -ano ^| findstr ":%%P" ^| findstr "LISTENING"') DO (
            taskkill /F /PID %%a >nul 2>&1
            IF !ERRORLEVEL! EQU 0 (
                ECHO [OK]   Killed process %%a on port %%P.
            ) ELSE (
                ECHO [FAIL] Could not kill process %%a on port %%P. Please close it manually.
                SET "PORTS_CLEARED=false"
            )
        )
    )
)

IF "!PORTS_CLEARED!"=="false" (
    ECHO [ERROR] Could not clear required ports. Aborting launch.
    PAUSE
    EXIT /B 1
)
ECHO [OK] All required ports are clear.
ECHO.

REM --- Phase 2: Launch Backend Service ---
ECHO [2/4] Starting backend Python service...
IF NOT EXIST .venv\Scripts\activate.bat (
    ECHO [ERROR] Virtual environment not found. Please run INSTALL_FORTUNA.bat first.
    PAUSE
    EXIT /B 1
)
start "Fortuna Backend" /B cmd /c "call .venv\Scripts\activate.bat && uvicorn python_service.api:app --host 127.0.0.1 --port %BACKEND_PORT% --log-level warning"
ECHO [OK] Backend service process started.
ECHO.

REM --- Phase 3: Wait for Backend Health ---
ECHO [3/4] Waiting for backend to become healthy...
SET /a ATTEMPTS=0
SET /a MAX_ATTEMPTS=30

:BackendHealthCheck
SET /a ATTEMPTS+=1
IF %ATTEMPTS% GTR %MAX_ATTEMPTS% (
    ECHO [ERROR] Backend failed to become healthy after 30 seconds. Check logs.
    PAUSE
    EXIT /B 1
)

REM Use PowerShell for a reliable HTTP check that is built into modern Windows
powershell -Command "(Invoke-WebRequest -Uri http://localhost:%BACKEND_PORT%/health -UseBasicParsing).StatusCode" 2>nul | findstr "200" >nul
IF !ERRORLEVEL! NEQ 0 (
    ECHO [INFO] Waiting... (!ATTEMPTS!/%MAX_ATTEMPTS%)
    timeout /t 1 /nobreak >nul
    GOTO BackendHealthCheck
)
ECHO [OK] Backend is healthy and operational!
ECHO.

REM --- Phase 4: Launch Frontend and Browser ---
ECHO [4/4] Starting frontend UI and launching browser...
start "Fortuna Frontend" /B cmd /c "cd web_platform\frontend && npm run dev"
timeout /t 5 /nobreak >nul
start http://localhost:%FRONTEND_PORT%
ECHO.
ECHO  ========================================================================
ECHO   LAUNCH COMPLETE!
ECHO  ========================================================================
ECHO.