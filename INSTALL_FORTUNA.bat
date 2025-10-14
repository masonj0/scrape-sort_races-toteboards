@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM ============================================================================
REM  FORTUNA ASCENDED - Bulletproof Windows Setup (v3.2)
REM  Includes: Pre-flight checks, dependency installation, parallel package setup, auto-recovery
REM ============================================================================

TITLE Fortuna Ascended - Setup Wizard v3.2

ECHO.
ECHO  ========================================================================
ECHO   FORTUNA ASCENDED - Bulletproof Installation Wizard
ECHO  ========================================================================
ECHO.

REM --- Main Execution Flow ---
SET "LAST_STEP="
CALL :CheckPrerequisites
IF %ERRORLEVEL% NEQ 0 GOTO :eof

:RunInstallCoreDependencies
SET "LAST_STEP=InstallCoreDependencies"
CALL :InstallCoreDependencies
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

:RunSetupVirtualEnv
SET "LAST_STEP=SetupVirtualEnv"
CALL :SetupVirtualEnv
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

:RunInstallPackagesParallel
SET "LAST_STEP=InstallPackagesParallel"
CALL :InstallPackagesParallel
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

:RunCreateShortcuts
SET "LAST_STEP=CreateShortcuts"
CALL :CreateShortcuts
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

ECHO.
ECHO  ========================================================================
ECHO   SETUP COMPLETE!
ECHO   Run 'LAUNCH_FORTUNA.bat' to start the application.
ECHO  ========================================================================
ECHO.
PAUSE
GOTO :eof

REM ============================================================================
REM  SUBROUTINES
REM ============================================================================

:CheckPrerequisites
    ECHO [1/5] Running pre-flight system checks...
    net session >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [FAIL] This installer requires Administrator privileges.
        echo  [FAIL] Please right-click and select "Run as Administrator"
        pause
        exit /b 1
    )
    FOR /f "tokens=4-5 delims=. " %%i IN ('ver') DO SET "WIN_VERSION=%%i.%%j"
    IF "!WIN_VERSION!" LSS "10.0" (
        ECHO [FAIL] Windows 10 or later is required. Your version: !WIN_VERSION!
        PAUSE
        EXIT /B 1
    )
    FOR /f "tokens=3" %%a IN ('dir /-c ^| find "bytes free"') DO SET "FREE_SPACE=%%a"
    SET "FREE_SPACE_NUM=%FREE_SPACE:,=%"
    IF %FREE_SPACE_NUM% LSS 2147483648 (
        ECHO [FAIL] Insufficient disk space. At least 2GB is required.
        PAUSE
        EXIT /B 1
    )
    ping -n 1 google.com >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [WARN] No internet connectivity detected. Installation may fail.
        CHOICE /C YN /M "Continue anyway?"
        IF ERRORLEVEL 2 EXIT /B 1
    )
    ECHO [OK] System prerequisites are met.
    ECHO.
    EXIT /B 0

:InstallCoreDependencies
    ECHO [2/5] Checking core dependencies (Python and Node.js)...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [INFO] Python not found! Installing Python 3.11...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\\python_installer.exe'"
        "%TEMP%\\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        del "%TEMP%\\python_installer.exe"
        echo  [OK] Python installed successfully!
    ) else (
        echo  [OK] Python is already installed.
    )
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [INFO] Node.js not found! Installing Node.js LTS...
        powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi' -OutFile '%TEMP%\\node_installer.msi'"
        msiexec /i "%TEMP%\\node_installer.msi" /quiet /norestart
        del "%TEMP%\\node_installer.msi"
        echo  [OK] Node.js installed successfully!
    ) else (
        echo  [OK] Node.js is already installed.
    )
    ECHO [OK] Core dependencies are present.
    ECHO.
    EXIT /B 0

:SetupVirtualEnv
    ECHO [3/5] Setting up Python virtual environment...
    IF NOT EXIST .venv (
        ECHO [INFO] Creating new virtual environment...
        python -m venv .venv
        IF %ERRORLEVEL% NEQ 0 (
            ECHO [FAIL] Failed to create Python virtual environment.
            EXIT /B 1
        )
    ) ELSE (
        ECHO [INFO] Existing virtual environment found.
    )
    ECHO [OK] Virtual environment is ready.
    ECHO.
    EXIT /B 0

:InstallPackagesParallel
    ECHO [4/5] Installing Python ^& Node.js dependencies in parallel...
    ECHO      Output is logged to pip_install.log and npm_install.log.

    start "Python Install" /B cmd /c "call .venv\\Scripts\\activate.bat && python -m pip install -r python_service\\requirements.txt > pip_install.log 2>&1"
    start "NPM Install" /B cmd /c "cd web_platform\\frontend && npm install > npm_install.log 2>&1"

    :WaitLoop
        tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Python Install" 2>NUL | find "cmd.exe" >NUL
        set PIP_RUNNING=%errorlevel%
        tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq NPM Install" 2>NUL | find "cmd.exe" >NUL
        set NPM_RUNNING=%errorlevel%
        IF %PIP_RUNNING%==0 GOTO :WaitLoopDelay
        IF %NPM_RUNNING%==0 GOTO :WaitLoopDelay
        GOTO :EndWaitLoop

    :WaitLoopDelay
        ECHO [INFO] Installation in progress... Please wait.
        timeout /t 5 /nobreak >nul
        GOTO :WaitLoop

    :EndWaitLoop
    ECHO [OK] Parallel installations complete. Checking logs...

    findstr /C:"Successfully installed" pip_install.log >nul
    SET PIP_SUCCESS=%errorlevel%
    findstr /C:"added" npm_install.log >nul
    SET NPM_SUCCESS=%errorlevel%

    IF %PIP_SUCCESS% NEQ 0 (
        ECHO [FAIL] Python package installation failed. Check pip_install.log.
        EXIT /B 1
    )
    IF %NPM_SUCCESS% NEQ 0 (
        ECHO [FAIL] Node.js package installation failed. Check npm_install.log.
        EXIT /B 1
    )
    ECHO [OK] All dependencies installed successfully.
    ECHO.
    EXIT /B 0

:CreateShortcuts
    ECHO [5/5] Creating desktop shortcuts...
    call CREATE_SHORTCUTS.bat
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [WARN] Could not create desktop shortcuts. You can run them manually from the project folder.
    ) ELSE (
        ECHO [OK] Desktop shortcuts created.
    )
    ECHO.
    EXIT /B 0

:ErrorHandler
    ECHO.
    ECHO  ========================================================================
    ECHO   [ERROR] SETUP FAILED on step: %LAST_STEP%
    ECHO  ========================================================================
    ECHO.
    ECHO  An error occurred. Please check the messages above or the log files.
    ECHO.
    CHOICE /C RF /N /M "Would you like to [R]etry the failed step or perform a [F]ull Reset?"

    IF ERRORLEVEL 2 GOTO :FullReset
    IF ERRORLEVEL 1 GOTO :RetryStep

:RetryStep
    ECHO [RETRY] Retrying step: %LAST_STEP%...
    GOTO Run%LAST_STEP%

:FullReset
    ECHO [RESET] Performing a full reset. Deleting potentially corrupted files...
    IF EXIST .venv (
        ECHO [RESET] Removing Python virtual environment...
        rmdir /s /q .venv 2>nul
    )
    IF EXIST web_platform\frontend\node_modules (
        ECHO [RESET] Removing Node.js modules...
        rmdir /s /q web_platform\frontend\node_modules 2>nul
    )
    ECHO [RESET] Complete. Please re-run this installer.
    ECHO.
    PAUSE
    EXIT /B 0
