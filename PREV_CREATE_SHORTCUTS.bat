@ECHO OFF
SETLOCAL
TITLE Fortuna Faucet - Shortcut Creator

ECHO.
ECHO =================================================
ECHO      Fortuna Faucet - Shortcut Creator
ECHO =================================================
ECHO.
ECHO This script will create a primary shortcut for the GUI Launcher on your Desktop.
ECHO.

REM Get the directory of the current script
SET "SCRIPT_DIR=%~dp0"

REM Use PowerShell to get the Desktop path dynamically
FOR /F "usebackq tokens=*" %%i IN (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) DO SET "DESKTOP_PATH=%%i"

IF NOT DEFINED DESKTOP_PATH ( ECHO [X] Could not determine Desktop path. && PAUSE && EXIT /B 1 )

ECHO - Creating 'Fortuna Faucet Control Panel' shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_PATH%\\Fortuna Faucet.lnk'); $s.TargetPath = '%SystemRoot%\\py.exe'; $s.Arguments = 'launcher_gui.pyw'; $s.IconLocation = '%SCRIPT_DIR%assets\\icon.ico'; $s.Description = 'Launch the Fortuna Faucet Control Panel'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

REM Rename .py to .pyw to run without a console window
IF EXIST launcher_gui.py ( ren launcher_gui.py launcher_gui.pyw )

ECHO.
ECHO =================================================
ECHO  Shortcut created successfully on your Desktop!
ECHO =================================================
ECHO.
PAUSE
ENDLOCAL