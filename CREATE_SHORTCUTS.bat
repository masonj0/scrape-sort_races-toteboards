@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Desktop Shortcut Creator
REM ============================================================================

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\\Desktop

echo Creating desktop shortcuts...

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\\Launch Fortuna Faucet.lnk'); $SC.TargetPath = '%SCRIPT_DIR%LAUNCH_FORTUNA.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,137'; $SC.Description = 'Launch Fortuna Faucet'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\\Fortuna Faucet Monitor.lnk'); $SC.TargetPath = '%SCRIPT_DIR%.venv\\Scripts\\python.exe'; $SC.Arguments = 'fortuna_monitor.py'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,23'; $SC.Description = 'Fortuna Faucet Status Monitor'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\\Stop Fortuna Faucet.lnk'); $SC.TargetPath = '%SCRIPT_DIR%STOP_FORTUNA.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,27'; $SC.Description = 'Stop Fortuna Faucet Services'; $SC.Save()"

echo Shortcuts created successfully!
