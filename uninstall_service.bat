@echo off
REM Stops and removes the Fortuna Faucet Windows Service.

echo Uninstalling Fortuna Faucet Windows Service...

REM Activate venv to ensure python command works as expected
call .\.venv\Scripts\activate.bat

REM Stop and remove the service
echo [1/2] Stopping the service...
python windows_service.py stop

echo [2/2] Removing the service from the registry...
python windows_service.py remove

echo.
echo ✅ Service stopped and uninstalled successfully!
echo.
pause
