# configure_startup.py
import winreg
import sys
from pathlib import Path

class StartupManager:
    """Manage Windows startup registry entries for the current user."""

    REGISTRY_PATH = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    APP_NAME = "FortunaFaucetTray"

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REGISTRY_PATH, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, cls.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    @classmethod
    def enable(cls):
        launcher_path = Path(__file__).parent / "launcher.ps1"
        cmd = f'powershell.exe -WindowStyle Hidden -File "{launcher_path}"'

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REGISTRY_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print("Startup enabled.")

    @classmethod
    def disable(cls):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REGISTRY_PATH, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, cls.APP_NAME)
            winreg.CloseKey(key)
            print("Startup disabled.")
        except FileNotFoundError:
            print("Already disabled.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'enable': StartupManager.enable()
        elif sys.argv[1] == 'disable': StartupManager.disable()
        elif sys.argv[1] == 'status': print(f"Startup is currently {'enabled' if StartupManager.is_enabled() else 'disabled'}")
    else:
        print("Usage: python configure_startup.py [enable|disable|status]")
