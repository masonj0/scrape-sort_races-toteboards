@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

REM ============================================================================
REM  FORTUNA FAUCET - Bulletproof Windows Setup (v4.1)
REM  Includes: Pre-flight checks, parallel installation, auto-recovery, config wizard
REM ============================================================================

TITLE Fortuna Faucet - Setup Wizard v4.1

ECHO.
ECHO  ========================================================================
ECHO   FORTUNA FAUCET - Bulletproof Installation Wizard
ECHO  ========================================================================
ECHO.

REM --- Main Execution Flow ---
CALL :CheckPrerequisites
IF %ERRORLEVEL% NEQ 0 GOTO :eof

CALL :SetupVirtualEnv
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

CALL :InstallPackagesParallel
IF %ERRORLEVEL% NEQ 0 GOTO ErrorHandler

CALL :RunConfigurationWizard
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
    ECHO [1/4] Running pre-flight system checks...
    ping -n 1 google.com >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [WARN] No internet connectivity detected. Installation may fail.
        CHOICE /C YN /M "Continue anyway?"
        IF ERRORLEVEL 2 EXIT /B 1
    )
    ECHO [OK] System prerequisites are met.
    ECHO.
    EXIT /B 0

:SetupVirtualEnv
    ECHO [2/4] Setting up Python virtual environment...
    IF NOT EXIST .venv ( python -m venv .venv )
    ECHO [OK] Virtual environment is ready.
    ECHO.
    EXIT /B 0

:InstallPackagesParallel
    ECHO [3/4] Installing all project dependencies in parallel...
    ECHO      Output is logged to pip_install.log, npm_install.log, and electron_install.log.

    start "Python Install" /B cmd /c "call .venv\Scripts\activate.bat && python -m pip install -r python_service\requirements.txt > pip_install.log 2>&1"
    start "NPM Install" /B cmd /c "cd web_platform\frontend && npm install > ..\..\npm_install.log 2>&1"
    start "Electron Install" /B cmd /c "cd electron && npm install > ..\electron_install.log 2>&1"

    :WaitLoop
        tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Python Install" 2>NUL | find "cmd.exe" >NUL
        set PIP_RUNNING=%errorlevel%
        tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq NPM Install" 2>NUL | find "cmd.exe" >NUL
        set NPM_RUNNING=%errorlevel%
        tasklist /FI "IMAGENAME eq cmd.exe" /FI "WINDOWTITLE eq Electron Install" 2>NUL | find "cmd.exe" >NUL
        set ELECTRON_RUNNING=%errorlevel%
        IF %PIP_RUNNING%==0 GOTO :WaitLoopDelay
        IF %NPM_RUNNING%==0 GOTO :WaitLoopDelay
        IF %ELECTRON_RUNNING%==0 GOTO :WaitLoopDelay
        GOTO :EndWaitLoop
    :WaitLoopDelay
        ECHO [INFO] Installation in progress... Please wait.
        timeout /t 5 /nobreak >nul
        GOTO :WaitLoop

    :EndWaitLoop
    ECHO [OK] Parallel installations complete. Checking logs...

    findstr /C:"Successfully installed" pip_install.log >nul
    IF %ERRORLEVEL% NEQ 0 ( ECHO [FAIL] Python installation failed. Check pip_install.log. && EXIT /B 1 )
    findstr /C:"added" npm_install.log >nul
    IF %ERRORLEVEL% NEQ 0 ( ECHO [FAIL] Node.js installation failed. Check npm_install.log. && EXIT /B 1 )
    findstr /C:"added" electron_install.log >nul
    IF %ERRORLEVEL% NEQ 0 ( ECHO [FAIL] Electron installation failed. Check electron_install.log. && EXIT /B 1 )

    ECHO [OK] All dependencies installed successfully.
    ECHO.
    EXIT /B 0

:RunConfigurationWizard
    ECHO [4/4] Running initial configuration wizard...
    call .venv\Scripts\activate.bat
    python setup_wizard.py
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [FAIL] Configuration wizard failed. Please check errors above.
        EXIT /B 1
    )
    ECHO [OK] Configuration complete.
    ECHO.
    EXIT /B 0

:ErrorHandler
    ECHO.
    ECHO  ========================================================================
    ECHO   [ERROR] SETUP FAILED!
    ECHO  ========================================================================
    ECHO.
    CHOICE /C RF /N /M "Would you like to [R]etry or perform a [F]ull Reset?"
    IF ERRORLEVEL 2 GOTO :FullReset
    IF ERRORLEVEL 1 GOTO :eof

:FullReset
    ECHO [RESET] Performing a full reset...
    IF EXIST .venv ( rmdir /s /q .venv 2>nul )
    IF EXIST web_platform\frontend\node_modules ( rmdir /s /q web_platform\frontend\node_modules 2>nul )
    IF EXIST electron\node_modules ( rmdir /s /q electron\node_modules 2>nul )
    ECHO [RESET] Complete. Please re-run this installer.
    PAUSE
    EXIT /B 0