@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Windows Native One-Click Installer (Unified)
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

echo  [1/6] Checking Python installation...
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
echo  [2/6] Checking Node.js installation...
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
echo  [3/6] Setting up Python virtual environment...
if not exist .venv (
    python -m venv .venv
    echo  [V] Virtual environment created!
) else (
    echo  [V] Virtual environment already exists!
)

echo.
echo  [4/6] Installing Python dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo  [V] Python packages installed!

echo.
echo  [5/6] Configuring the application...
if not exist .env (
    echo  [!] .env file not found!
    echo  [*] Launching interactive setup wizard for first-time configuration...
    python setup_wizard.py
    echo  [V] Configuration created!
) else (
    echo  [V] Existing .env configuration found! Skipping wizard.
)

echo.
echo  [6/6] Installing Node.js dependencies...
cd web_platform\frontend
call npm install --silent
cd ..\..
echo  [V] Node.js packages installed!

echo.
echo  [*] Creating desktop shortcuts...
call CREATE_SHORTCUTS.bat

echo.
echo  ========================================================================
echo   INSTALLATION COMPLETE!
echo  ========================================================================
echo.
echo   To start the application, double-click the 'Launch Fortuna'
_   shortcut on your desktop.
_echo.
pause
