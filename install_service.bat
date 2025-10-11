@echo off
REM Installs and starts the Fortuna Faucet backend as a Windows Service.

echo Installing Fortuna Faucet as a Windows Service...

REM Ensure pywin32 is installed in the venv
echo [1/2] Verifying pywin32 dependency...
call .\.venv\Scripts\activate.bat
pip install pywin32 --quiet

REM Install and start the service
echo [2/2] Installing and starting the service...
python windows_service.py install
python windows_service.py start

echo.
echo ✅ Service installed and started successfully!
echo The backend will now run automatically in the background.
echo You can manage it from the Windows Services application (services.msc).
echo.
pause
