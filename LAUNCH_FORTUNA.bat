@echo off
REM ============================================================================
REM  FORTUNA FAUCET - Windows Native Launcher (Tray Edition)
REM ============================================================================

title Fortuna Faucet - Launcher
color 0B

echo.
echo  ========================================================================
echo   FORTUNA FAUCET - System Tray Launcher
echo  ========================================================================
echo.

echo  [*] Launching Fortuna Faucet in the system tray...
echo  [*] The backend service will continue running in the background.

REM Use pythonw.exe to run the script without a console window
call .\\.venv\\Scripts\\activate.bat
start "Fortuna Tray App" /B pythonw.exe fortuna_tray.py

echo.
echo  [V] Fortuna Faucet is now running in your system tray.
_echo  [V] Right-click the icon for options.
_echo.
pause
