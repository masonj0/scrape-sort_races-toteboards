@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Desktop Shortcut Creator
REM ============================================================================

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\\Desktop

echo Creating desktop shortcuts...

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\\Launch Fortuna Faucet.lnk'); $SC.TargetPath = '%SCRIPT_DIR%LAUNCH_FORTUNA.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,137'; $SC.Description = 'Launch Fortuna Faucet'; $SC.Save()"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\\Launch Monitor.lnk'); $s.TargetPath = 'cmd.exe'; $s.Arguments = '/c \"call %SCRIPT_DIR%.venv\\Scripts\\activate.bat && python %SCRIPT_DIR%fortuna_monitor.py\"'; $s.IconLocation = '%%SystemRoot%%\\System32\\imageres.dll,102'; $s.Description = 'Launch the Fortuna Monitor GUI'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%DESKTOP%\\Stop Fortuna Faucet.lnk'); $SC.TargetPath = '%SCRIPT_DIR%STOP_FORTUNA.bat'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,27'; $SC.Description = 'Stop Fortuna Faucet Services'; $SC.Save()"

echo Shortcuts created successfully!
