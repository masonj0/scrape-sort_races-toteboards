@echo off
REM This script compiles the WiX project into an MSI installer.

REM Assumes WiX Toolset v3.14 is installed in the default location.
set WIX_PATH="C:\Program Files (x86)\WiX Toolset v3.14\bin"

if not exist %WIX_PATH% (
    echo [ERROR] WiX Toolset not found. Please install it to build the MSI.
    goto :eof
)

echo [INFO] Compiling WiX source file (fortuna_faucet_installer.wxs)...
%WIX_PATH%\candle.exe fortuna_faucet_installer.wxs -out fortuna.wixobj
if %errorlevel% neq 0 ( GOTO :error )

echo [INFO] Linking WiX object file into an MSI package...
%WIX_PATH%\light.exe fortuna.wixobj -out ..\dist\FortunaFaucet_Setup.msi
if %errorlevel% neq 0 ( GOTO :error )

echo [SUCCESS] Installer 'FortunaFaucet_Setup.msi' created successfully in the 'dist' folder.
goto :eof

:error
echo [ERROR] Failed to build the installer.
pause
:eof