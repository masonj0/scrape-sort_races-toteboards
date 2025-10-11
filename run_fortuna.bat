@echo off
TITLE Fortuna Faucet Launcher

REM This script now delegates to the enhanced PowerShell launcher.
REM It ensures the correct execution policy is set for the current process.

ECHO Launching Fortuna Faucet via enhanced PowerShell launcher...
powershell -ExecutionPolicy Bypass -File .\\launcher.ps1

ECHO.
PAUSE
