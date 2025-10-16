@ECHO OFF
TITLE Fortuna Faucet - Master MSI Builder

REM --- Phase 1: Administrator Check ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
IF '%errorlevel%' NEQ '0' ( ECHO [ERROR] Administrator privileges are required. && PAUSE && EXIT /B 1 )

ECHO.
ECHO =================================================
ECHO  Fortuna Faucet - Master MSI Installer Builder
ECHO =================================================
ECHO.

REM --- Phase 2: Pre-Flight Checks ---
ECHO [1/4] Running pre-flight environment checks...
npm -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 ( ECHO [FAIL] Node.js (npm) is not found. && PAUSE && EXIT /B 1 )
IF NOT EXIST .venv\Scripts\activate.bat ( ECHO [FAIL] Python environment not found. Please run INSTALL_FORTUNA.bat once. && PAUSE && EXIT /B 1 )
ECHO [OK] Environment is ready for build.
ECHO.

ECHO [2/4] Installing/Verifying Node.js dependencies...
ECHO  - Frontend...
cd web_platform\frontend && npm install && cd ..\..
ECHO  - Electron...
cd electron && npm install && cd ..
ECHO [OK] Node.js dependencies are up to date.
ECHO.

ECHO Press any key to begin the build process...
PAUSE > NUL

ECHO.
ECHO [3/4] Building the MSI installer via electron-builder...
ECHO This may take several minutes. Please be patient.
ECHO.
cd electron
npm run dist
IF %ERRORLEVEL% NEQ 0 ( ECHO [X] FAILED to build the MSI installer. && cd .. && PAUSE && EXIT /B 1 )
cd ..

ECHO.
ECHO [4/4] Moving final MSI to project root...
FOR /F "delims=" %%i IN ('dir /b electron\dist\*.msi') DO (
    MOVE /Y "electron\dist\%%i" . > NUL
    ECHO [V] The installer [%%i] has been moved to the project root directory.
)
ECHO.

ECHO =================================================
ECHO  BUILD SUCCESSFUL!
ECHO =================================================
ECHO.
PAUSE