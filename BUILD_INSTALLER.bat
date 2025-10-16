@ECHO OFF
TITLE Fortuna Faucet - MSI Installer Builder v2.0

REM --- Phase 1: Administrator Check ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
IF '%errorlevel%' NEQ '0' (
    ECHO.
    ECHO [ERROR] Administrator privileges are required to run this build script.
    ECHO         Please right-click this script and select 'Run as administrator'.
    ECHO.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO =================================================
ECHO  Fortuna Faucet - MSI Installer Builder
ECHO =================================================
ECHO.

REM --- Phase 2: Pre-Flight Checks ---
ECHO [1/3] Running pre-flight environment checks...
npm -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [FAIL] Node.js (npm) is not found in your system's PATH.
    ECHO [INFO] Please run INSTALL_FORTUNA.bat to set up the environment.
    PAUSE
    EXIT /B 1
)
IF NOT EXIST electron\node_modules (
    ECHO [FAIL] Electron's Node.js dependencies are not installed.
    ECHO [INFO] Please run INSTALL_FORTUNA.bat to set up the environment.
    PAUSE
    EXIT /B 1
)
ECHO [OK] Environment is ready for build.
ECHO.

ECHO Press any key to begin the build process...
PAUSE > NUL

ECHO.
ECHO [2/3] Building the MSI installer...
ECHO This may take several minutes. Please be patient.
ECHO.
pushd electron
npm run dist
IF %ERRORLEVEL% NEQ 0 (
    ECHO [X] FAILED to build the MSI installer. Please check the output above for errors.
    popd
    PAUSE
    EXIT /B 1
)
popd

ECHO.
ECHO [3/3] Moving MSI installer to project root...
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