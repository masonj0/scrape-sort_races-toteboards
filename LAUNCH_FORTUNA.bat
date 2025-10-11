@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Windows Native Launcher (Ultimate Edition)
REM ============================================================================

title Fortuna Faucet - Startup Sequence
color 0B

echo.
echo  ========================================================================
echo   FORTUNA FAUCET - System Startup
echo  ========================================================================
echo.

if not exist .env (
    echo  [!] WARNING: .env file not found!
    echo  [!] Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

echo  [*] Starting Python Backend API...
start "Fortuna Backend" /MIN cmd /c "call .venv\\Scripts\\activate.bat && uvicorn python_service.api:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo  [*] Starting Next.js Frontend...
start "Fortuna Frontend" /MIN cmd /c "cd web_platform\\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo  [*] Starting Status Monitor...
start "Fortuna Monitor" cmd /c "call .venv\\Scripts\\activate.bat && python fortuna_monitor.py"

timeout /t 3 /nobreak >nul

echo  [*] Opening Dashboard in Browser...
start "" "http://localhost:3000"

echo.
echo  ========================================================================
echo   ALL SYSTEMS OPERATIONAL
echo  ========================================================================
echo.
pause
