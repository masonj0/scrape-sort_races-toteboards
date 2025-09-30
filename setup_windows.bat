@ECHO OFF
SETLOCAL

:: ==============================================================================
:: == Checkmate V8: Penta-Hybrid Environment Setup Script
:: ==============================================================================
:: This script verifies that all necessary dependencies and SDKs for the
:: entire Penta-Hybrid architecture are installed.
::
:: Required: Python, Rust, .NET SDK, Node.js
:: ==============================================================================

ECHO.
ECHO [SETUP] Starting Checkmate V8 Environment Verification...
ECHO ==========================================================

:check_python
ECHO.
ECHO [1/4] Verifying Python and Pip...
WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Python is not found in the system PATH. Please install Python 3.10+.
    GOTO :error
)
WHERE pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Pip is not found in the system PATH. Please ensure Python is installed correctly.
    GOTO :error
)
ECHO [SUCCESS] Python and Pip are installed.
ECHO [SETUP] Installing Python dependencies from requirements.txt...
CALL pip install -r python_service\requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Failed to install Python dependencies.
    GOTO :error
)
ECHO [SUCCESS] Python dependencies installed.

:check_rust
ECHO.
ECHO [2/4] Verifying Rust and Cargo...
WHERE cargo >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Cargo is not found in the system PATH. Please install the Rust toolchain.
    GOTO :error
)
ECHO [SUCCESS] Rust toolchain is installed.

:check_dotnet
ECHO.
ECHO [3/4] Verifying .NET SDK...
WHERE dotnet >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] .NET SDK is not found in the system PATH. Please install the .NET 6.0 SDK or newer.
    GOTO :error
)
ECHO [SUCCESS] .NET SDK is installed.

:check_node
ECHO.
ECHO [4/4] Verifying Node.js and NPM...
WHERE npm >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] NPM is not found in the system PATH. Please install Node.js.
    GOTO :error
)
ECHO [SUCCESS] Node.js and NPM are installed.
ECHO [SETUP] Installing TypeScript dependencies for API Gateway...
CALL npm --prefix web_platform\api_gateway install
IF %ERRORLEVEL% NEQ 0 GOTO :error
ECHO [SETUP] Installing TypeScript dependencies for Frontend...
CALL npm --prefix web_platform\frontend install
IF %ERRORLEVEL% NEQ 0 GOTO :error
ECHO [SUCCESS] TypeScript dependencies installed.

ECHO.
ECHO ==========================================================
ECHO [SUCCESS] All Checkmate V8 environment dependencies are present and configured!
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