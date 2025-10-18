@echo off
setlocal

echo =================================================
echo  Checkmate V7 Launcher
echo =================================================
echo.

REM Check for venv
if not exist venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found.
    echo Please run 'setup_windows.bat' first.
    goto :eof
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Launching Checkmate V7 components in separate windows...
echo Please close all three windows to shut down the application.
echo.

REM Launch Redis Server
start "Redis Server" redis-server

REM Launch Celery Worker
start "Celery Worker" celery -A src.checkmate_v7.services.celery_app worker --loglevel=info

REM Launch Uvicorn API Server
start "Uvicorn API Server" uvicorn src.checkmate_v7.api:app --host 0.0.0.0 --port 8000

echo.
echo All components launched.
echo.

endlocal
pause
