@echo off
REM ============================================================================
REM  Fortuna Faucet: Common Issues Auto-Fix
REM ============================================================================

:menu
cls
echo ========================================
echo   Fortuna Faucet - Auto-Fix Utility
echo ========================================
echo.

echo Select an issue to fix:
echo.
echo 1. Recreate virtual environment
echo 2. Clear Python cache files
echo 3. Reinstall frontend dependencies
echo 4. Kill stuck processes (ports 8000, 3000)
echo 5. Reset database
echo 6. Run all fixes
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto fix_venv
if "%choice%"=="2" goto fix_cache
if "%choice%"=="3" goto fix_frontend
if "%choice%"=="4" goto fix_ports
if "%choice%"=="5" goto fix_database
if "%choice%"=="6" goto fix_all
if "%choice%"=="7" goto end

:fix_venv
echo.
echo [FIX] Recreating virtual environment...
if exist .venv (
    echo Removing old virtual environment...
    rmdir /s /q .venv
)
python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r python_service\requirements.txt
echo [DONE] Virtual environment recreated
if not "%choice%"=="6" pause & goto end
goto fix_cache

:fix_cache
echo.
echo [FIX] Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo [DONE] Cache cleared
if not "%choice%"=="6" pause & goto end
goto fix_frontend

:fix_frontend
echo.
echo [FIX] Reinstalling frontend dependencies...
cd web_platform\frontend
if exist node_modules (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)
call npm install
cd ..\..
echo [DONE] Frontend dependencies reinstalled
if not "%choice%"=="6" pause & goto end
goto fix_ports

:fix_ports
echo.
echo [FIX] Killing stuck processes...

REM Kill process on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /F /PID %%a 2>nul
)

REM Kill process on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do (
    taskkill /F /PID %%a 2>nul
)

echo [DONE] Processes killed
if not "%choice%"=="6" pause & goto end
goto fix_database

:fix_database
echo.
echo [FIX] Resetting database...
echo WARNING: This will delete all stored race data!
set /p confirm="Are you sure? (Y/N): "
if /i not "%confirm%"=="Y" goto skip_db

if exist data\fortuna.db (
    del data\fortuna.db
    echo Database deleted
)

call .venv\Scripts\activate.bat
python -c "from python_service.models import Base; from sqlalchemy import create_engine; engine = create_engine('sqlite:///data/fortuna.db'); Base.metadata.create_all(engine); print('Database recreated')"
echo [DONE] Database reset

:skip_db
if not "%choice%"=="6" pause & goto end

:fix_all
goto end

:end
echo.
echo ========================================
echo   Fix Complete
echo ========================================
pause