@echo off
REM Installs and starts the Fortuna Faucet backend as a Windows Service.

echo Installing Fortuna Faucet as a Windows Service...

REM Ensure pywin32 is installed in the venv
call .venv\Scripts\activate.bat
pip install pywin32 --quiet

REM Install the service
python windows_service.py install

REM Start the service
python windows_service.py start

echo.
echo Service installed and started successfully!
echo The backend will now run automatically in the background.
pause
