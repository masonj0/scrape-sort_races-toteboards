# fortuna_tray.py
# Provides a native Windows System Tray icon and menu for Fortuna Faucet.

import pystray
import configparser
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import webbrowser
import subprocess
from pathlib import Path

class FortunaTrayApp:
    def __init__(self):
        self.icon = None
        self.project_root = Path(__file__).parent.resolve()

    def create_icon(self) -> Image.Image:
        width = 64
        height = 64
        # Using a gold color for the icon background
        image = Image.new('RGB', (width, height), color='#FFD700')
        dc = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        dc.text((12, 15), "FF", font=font, fill='black')
        return image

    def on_quit(self, icon, item):
        icon.stop()
        # Execute the main stop script to ensure all services are terminated
        subprocess.Popen(str(self.project_root / "STOP_FORTUNA.bat"), shell=True)

    def on_open_dashboard(self, icon, item):
        webbrowser.open('http://localhost:3000')

    def on_show_monitor(self, icon, item):
        # Launch the Tkinter monitor
        python_exe = self.project_root / ".venv" / "Scripts" / "python.exe"
        monitor_script = self.project_root / "fortuna_monitor.py"
        subprocess.Popen([str(python_exe), str(monitor_script)])

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem('Open Dashboard', self.on_open_dashboard, default=True),
            pystray.MenuItem('Show Monitor', self.on_show_monitor),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit Fortuna', self.on_quit)
        )

        self.icon = pystray.Icon(
            "Fortuna Faucet",
            self.create_icon(),
            "Fortuna Faucet - Racing Intelligence",
            menu
        )

        self.icon.run()

def validate_configuration():
    """
    Reads config.ini and ensures all required sections and keys are present.
    Raises ValueError if a required setting is missing.
    """
    config = configparser.ConfigParser()
    if not config.read('config.ini'):
        raise ValueError("CRITICAL: config.ini file not found or is empty.")

    # Define all settings required for the application to function
    required_settings = {
        'API_KEYS': ['betfair_api_key'],
        'SETTINGS': ['database_path', 'log_level']
    }

    missing_items = []
    for section, keys in required_settings.items():
        if not config.has_section(section):
            missing_items.append(f"Missing section: [{section}]")
            continue
        for key in keys:
            if not config.has_option(section, key) or not config.get(section, key):
                missing_items.append(f"Missing or empty key '{key}' in section [{section}]")

    if missing_items:
        error_message = "Configuration Error! Please fix the following issues in config.ini before launching:\n\n"
        error_message += "\n".join(f"- {item}" for item in missing_items)
        raise ValueError(error_message)

def main():
    """Main function to validate config and run the application."""
    try:
        validate_configuration()
    except (ValueError, configparser.Error) as e:
        # Hide the redundant root tkinter window
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fortuna Ascended - Configuration Error", str(e))
        sys.exit(1)

    # If validation passes, proceed to create and run the tray icon
    app = FortunaTrayApp()
    app.run()

if __name__ == "__main__":
    main()
