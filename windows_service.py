# windows_service.py
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess
from pathlib import Path

class FortunaBackendService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FortunaFaucetBackend"
    _svc_display_name_ = "Fortuna Faucet Racing Analysis Service"
    _svc_description_ = "Background service for continuous racing data monitoring."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.backend_process = None
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.backend_process:
            self.backend_process.terminate()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()

    def main(self):
        install_dir = Path(__file__).parent.resolve()
        venv_python = install_dir / ".venv" / "Scripts" / "python.exe"
        api_module_dir = install_dir / "python_service"

        env = os.environ.copy()
        env_file = install_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value.strip('\"')

        self.backend_process = subprocess.Popen(
            [str(venv_python), "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(api_module_dir),
            env=env
        )

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FortunaBackendService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FortunaBackendService)
