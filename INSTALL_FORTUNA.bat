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
echo  [4/5] Installing Python dependencies...
pushd python_service
IF NOT EXIST requirements.txt (
    ECHO [X] CRITICAL: requirements.txt not found in python_service folder!
    popd
    exit /b 1
)
call ..\\.venv\\Scripts\\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
IF %ERRORLEVEL% NEQ 0 (
    ECHO [X] FAILED to install Python dependencies. Please check your Python and pip installation.
    popd
    exit /b 1
)
popd
echo  [V] Python packages installed!

echo.
echo  [5/5] Installing Node.js dependencies...
pushd web_platform\\frontend
IF NOT EXIST package.json (
    ECHO [X] CRITICAL: package.json not found in web_platform\\frontend folder!
    popd
    exit /b 1
)
npm install
IF %ERRORLEVEL% NEQ 0 (
    ECHO [X] FAILED to install Node.js dependencies. Please ensure Node.js is installed and in your system PATH.
    popd
    exit /b 1
)
popd
echo  [V] Node.js packages installed!

echo.
echo  [*] Creating desktop shortcuts...
call CREATE_SHORTCUTS.bat

echo.
echo  ========================================================================
echo   INSTALLATION COMPLETE!
echo  ========================================================================
echo.
pause
