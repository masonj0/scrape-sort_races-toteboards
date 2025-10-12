# fortuna_tray.py
# Provides a native Windows System Tray icon and menu for Fortuna Faucet.

import pystray
from PIL import Image, ImageDraw
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
        # dc.text((12, 15), "FF", fill='black') # Temporarily removed due to font loading issues
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

if __name__ == '__main__':
    app = FortunaTrayApp()
    app.run()
