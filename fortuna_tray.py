# fortuna_tray.py - Enhanced with Auto-Updates and Full Control

import pystray
from PIL import Image
import subprocess
import os
import sys
import threading
import webbrowser
import requests

# --- Configuration ---
VERSION_FILE = "VERSION.txt"
GITHUB_REPO = "masonj0/scrape-sort_races-toteboards"
CURRENT_VERSION = "0.0.0" # Default if file not found

# --- Helper Functions ---
def get_root_path():
    """Gets the project's root directory."""
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

def get_script_path(script_name):
    """Gets the absolute path to a script in the project root."""
    return os.path.join(get_root_path(), script_name)

def run_script(script_name):
    """Runs a batch script in a new console window."""
    subprocess.Popen(["cmd", "/c", f'start "{script_name}" "{get_script_path(script_name)}"'], shell=True)

def get_current_version():
    """Reads the version from the VERSION.txt file."""
    try:
        with open(get_script_path(VERSION_FILE), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return CURRENT_VERSION

def show_toast(title, message, callback=None):
    """Shows a Windows toast notification in a thread-safe way."""
    def _show():
        try:
            from windows_toasts import Toast, WindowsToaster
            toaster = WindowsToaster(title)
            new_toast = Toast()
            new_toast.text_fields = [message]
            if callback:
                new_toast.on_activated = lambda _: callback()
            toaster.show_toast(new_toast)
        except (ImportError, RuntimeError):
            print(f"[TOAST] {title}: {message}") # Fallback for non-Windows or errors

    # Run in a separate thread to avoid blocking the main UI
    threading.Thread(target=_show, daemon=True).start()

def _do_update_check():
    """The actual worker function for checking updates."""
    show_toast("Fortuna Faucet", "Checking for updates...")
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()

        latest_release = response.json()
        latest_version = latest_release['tag_name'].lstrip('v')
        current_version = get_current_version()

        # Simple version comparison
        if latest_version > current_version:
            download_url = latest_release['html_url']
            show_toast(
                "Update Available!",
                f"Version {latest_version} is available. Click here to download.",
                callback=lambda: webbrowser.open(download_url)
            )
        else:
            show_toast("Fortuna Faucet", f"You are running the latest version ({current_version}).")
    except Exception as e:
        show_toast("Update Check Failed", "Could not connect to GitHub.")

# --- Tray Icon Actions ---
def check_for_updates(icon, item):
    """Starts the update check in a separate thread to keep the UI responsive."""
    threading.Thread(target=_do_update_check, daemon=True).start()

def open_service_manager(icon, item):
    run_script("SERVICE_MANAGER.bat")

def on_exit(icon, item):
    icon.stop()

# --- Main Execution ---
if __name__ == "__main__":
    try:
        image = Image.open(get_script_path("assets/icon.ico"))
    except FileNotFoundError:
        image = Image.new('RGB', (64, 64), color='blue') # Fallback icon

    menu = pystray.Menu(
        pystray.MenuItem('Open Service Manager', open_service_manager, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Check for Updates', check_for_updates),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', on_exit)
    )

    icon = pystray.Icon("FortunaFaucet", image, "Fortuna Faucet", menu)
    icon.run()