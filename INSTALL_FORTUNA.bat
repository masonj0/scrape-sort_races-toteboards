@ECHO OFF
REM DEPRECATED FOR USERS - This script is now for DEVELOPER USE ONLY.
REM The primary installation method for users is the .msi installer.

TITLE Fortuna Faucet - Developer Environment Setup

ECHO.
ECHO  ========================================================================
ECHO   Fortuna Faucet - Developer Environment Setup
ECHO  ========================================================================
ECHO.
ECHO   This script will set up the Python and Node.js environments required
ECHO   to run and develop the Fortuna Faucet application from source.
ECHO.
PAUSE

REM (The core logic remains for developers, but the user-facing language is gone)
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r python_service\requirements.txt
cd web_platform\frontend && npm install && cd ..\..
cd electron && npm install && cd ..

ECHO.
ECHO  [SUCCESS] Developer environment setup is complete.
ECHO  You can now use 'launcher_gui.pyw' to run the application.
ECHO.
PAUSE