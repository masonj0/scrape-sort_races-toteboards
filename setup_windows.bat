@ECHO OFF
SETLOCAL

:: ==============================================================================
:: == Checkmate Ultimate Solo - Environment Setup Script
:: ==============================================================================
:: This script verifies and installs dependencies for the final, two-pillar
:: architecture: Python and Node.js.
:: ==============================================================================

ECHO.
ECHO [SETUP] Starting Checkmate Ultimate Solo Environment Verification...
ECHO ==========================================================

:check_python
ECHO.
ECHO [1/2] Verifying Python and installing dependencies...
WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Python not found. Please install Python 3.10+ & GOTO :error)

CALL pip install -r python_service\requirements.txt
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Failed to install Python dependencies. & GOTO :error)
ECHO [SUCCESS] Python dependencies installed.

:check_node
ECHO.
ECHO [2/2] Verifying Node.js and installing dependencies...
WHERE npm >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] NPM not found. Please install Node.js. & GOTO :error)

CALL npm --prefix web_platform\frontend install
IF %ERRORLEVEL% NEQ 0 GOTO :error
ECHO [SUCCESS] TypeScript dependencies installed.

ECHO.
ECHO ==========================================================
ECHO [SUCCESS] All Ultimate Solo environment dependencies are present and configured!
ECHO ==========================================================
GOTO :eof

:error
ECHO.
ECHO ==========================================================
ECHO [FAILURE] Environment setup failed. Please correct the errors above and re-run.
ECHO ==========================================================
EXIT /B 1

:eof
ENDLOCAL
