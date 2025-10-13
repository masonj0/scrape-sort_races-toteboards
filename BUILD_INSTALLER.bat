@ECHO OFF
TITLE Fortuna Ascended - MSI Installer Builder
ECHO.
ECHO =================================================
ECHO  Fortuna Ascended - MSI Installer Builder
ECHO =================================================
ECHO.
ECHO This script will build the distributable MSI installer using electron-builder.
ECHO The final installer will be located in the 'electron\dist' directory.
ECHO.
ECHO Press any key to begin the build process...
PAUSE > NUL

ECHO.
ECHO [1/2] Navigating to the Electron directory...
pushd electron
IF %ERRORLEVEL% NEQ 0 (
    ECHO [X] FAILED to navigate to the 'electron' directory.
    exit /b 1
)
ECHO [V] Success!
ECHO.

ECHO [2/2] Building the MSI installer...
ECHO This may take several minutes. Please be patient.
ECHO.
npm run dist
IF %ERRORLEVEL% NEQ 0 (
    ECHO [X] FAILED to build the MSI installer. Please check the output above for errors.
    ECHO Ensure Node.js is installed and you have run 'npm install' in the 'electron' directory first.
    popd
    exit /b 1
)
ECHO.
ECHO =================================================
ECHO  BUILD SUCCESSFUL!
ECHO =================================================
ECHO.
ECHO The MSI installer can be found in the 'electron\dist' directory.
ECHO.
popd
PAUSE
