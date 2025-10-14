@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Windows Native One-Click Installer
REM ============================================================================

title Fortuna Faucet - Installation Wizard
color 0A
echo.
echo  ========================================================================
echo   FORTUNA FAUCET - Automated Installation Wizard
echo  ========================================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] This installer requires Administrator privileges.
    echo  [!] Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [X] Python not found! Installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\\python_installer.exe'"
    "%TEMP%\\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\\python_installer.exe"
    echo  [V] Python installed successfully!
) else (
    echo  [V] Python found!
)

echo.
echo  [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [X] Node.js not found! Installing Node.js LTS...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi' -OutFile '%TEMP%\\node_installer.msi'"
    msiexec /i "%TEMP%\\node_installer.msi" /quiet /norestart
    del "%TEMP%\\node_installer.msi"
    echo  [V] Node.js installed successfully!
) else (
    echo  [V] Node.js found!
)

echo.
echo  [3/5] Setting up Python virtual environment...
if not exist .venv (
    python -m venv .venv
    echo  [V] Virtual environment created!
) else (
    echo  [V] Virtual environment already exists!
)

echo.
ECHO [4/5] Installing Python & Node.js dependencies in parallel...
ECHO      Output is logged to pip_install.log and npm_install.log in the root directory.

REM Run installations in the background of the current console window
start "Python Install" /B cmd /c "call .venv\Scripts\activate.bat && python -m pip install -r python_service\requirements.txt > pip_install.log 2>&1"
start "NPM Install" /B cmd /c "cd web_platform\frontend && npm install > npm_install.log 2>&1"

:WaitLoop
    REM Check if the processes are still running by looking for their window titles
    tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Python Install" 2>NUL | find "cmd.exe" >NUL
    set PIP_RUNNING=%errorlevel%
    tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq NPM Install" 2>NUL | find "cmd.exe" >NUL
    set NPM_RUNNING=%errorlevel%

    IF %PIP_RUNNING%==0 (
        ECHO [INFO] Python installation is in progress...
    )
    IF %NPM_RUNNING%==0 (
        ECHO [INFO] Node.js installation is in progress...
    )

    REM If either is running, wait and loop again
    IF %PIP_RUNNING%==0 GOTO :WaitLoopDelay
    IF %NPM_RUNNING%==0 GOTO :WaitLoopDelay
    GOTO :EndWaitLoop

:WaitLoopDelay
    timeout /t 5 /nobreak >nul
    GOTO :WaitLoop

:EndWaitLoop
ECHO [OK] Parallel installations complete. Checking logs...

REM Check pip log for errors. A success log is usually very long.
findstr /C:"Successfully installed" pip_install.log >nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Python package installation may have failed. Please check pip_install.log for details.
    REM Do not exit, as npm might have succeeded and user can debug.
)

REM Check npm log for success message.
findstr /C:"added" npm_install.log >nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [WARN] Could not confirm successful npm package installation. Please check npm_install.log.
)

echo.
echo  [5/5] Creating desktop shortcuts...
call CREATE_SHORTCUTS.bat

echo.
echo  ========================================================================
echo   INSTALLATION COMPLETE!
echo  ========================================================================
echo.
pause
