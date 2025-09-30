@ECHO OFF
SETLOCAL

:: ==============================================================================
:: == Checkmate V8: Penta-Hybrid Environment Setup & Verification Script
:: ==============================================================================

ECHO.
ECHO [SETUP] Starting Checkmate V8 Environment Verification...
ECHO ==========================================================

:check_python
ECHO.
ECHO [1/4] Verifying Python and installing dependencies...
WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Python not found. Please install Python 3.10+ & GOTO :error)

CALL pip install -r python_service\requirements.txt
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Failed to install Python dependencies. & GOTO :error)
ECHO [SUCCESS] Python dependencies installed.

:check_rust
ECHO.
ECHO [2/4] Verifying Rust and Cargo...
WHERE cargo >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Cargo not found. Please install the Rust toolchain. & GOTO :error)
ECHO [SUCCESS] Rust toolchain is installed.

:check_dotnet
ECHO.
ECHO [3/4] Verifying .NET SDK...
WHERE dotnet >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] .NET SDK not found. Please install the .NET 6.0 SDK or newer. & GOTO :error)
ECHO [SUCCESS] .NET SDK is installed.

:check_node
ECHO.
ECHO [4/4] Verifying Node.js and installing dependencies...
WHERE npm >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] NPM not found. Please install Node.js. & GOTO :error)

CALL npm --prefix web_platform\api_gateway install
IF %ERRORLEVEL% NEQ 0 GOTO :error
CALL npm --prefix web_platform\frontend install
IF %ERRORLEVEL% NEQ 0 GOTO :error
ECHO [SUCCESS] TypeScript dependencies installed.

:verify_ruff
ECHO.
ECHO [VERIFY] Verifying Python code quality with Ruff...
WHERE ruff >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (ECHO [ERROR] Ruff not found. Please ensure it was in requirements. & GOTO :error)
CALL ruff check .
ECHO [SUCCESS] Ruff code quality check complete.

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