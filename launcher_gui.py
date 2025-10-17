import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time
import requests
import psutil
from pathlib import Path

class FortunaLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐴 Fortuna Faucet - System Control")
        self.geometry("600x400")
        self.configure(bg='#1a1a2e')
        # self.iconbitmap(default='fortuna.ico') # Icon file needs to be created

        self.backend_proc = None
        self.frontend_proc = None

        self._create_ui()
        self._check_services()

    def _create_ui(self):
        """Create launcher UI"""
        # Title
        title = tk.Label(
            self,
            text="🐴 Fortuna Faucet",
            font=("Segoe UI", 20, "bold"),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        title.pack(pady=20)

        # Status Indicators
        status_frame = tk.Frame(self, bg='#1a1a2e')
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        # Backend Status
        tk.Label(status_frame, text="Backend:", bg='#1a1a2e', fg='#ffffff').pack(anchor="w")
        self.backend_status = tk.Canvas(status_frame, width=300, height=40, bg='#0f3460', highlightthickness=0)
        self.backend_status.pack(fill=tk.X, pady=(0, 10))
        self.backend_indicator = self.backend_status.create_oval(10, 5, 30, 25, fill='#ff4444')
        self.backend_text = self.backend_status.create_text(50, 15, text="Starting...", fill='#ffffff', anchor="w")

        # Frontend Status
        tk.Label(status_frame, text="Frontend:", bg='#1a1a2e', fg='#ffffff').pack(anchor="w")
        self.frontend_status = tk.Canvas(status_frame, width=300, height=40, bg='#0f3460', highlightthickness=0)
        self.frontend_status.pack(fill=tk.X)
        self.frontend_indicator = self.frontend_status.create_oval(10, 5, 30, 25, fill='#ff4444')
        self.frontend_text = self.frontend_status.create_text(50, 15, text="Starting...", fill='#ffffff', anchor="w")

        # Control Buttons
        button_frame = tk.Frame(self, bg='#1a1a2e')
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        self.launch_btn = tk.Button(
            button_frame,
            text="▶ START FORTUNA",
            font=("Segoe UI", 14, "bold"),
            bg='#00ff88',
            fg='#000000',
            command=self.launch_services,
            height=2
        )
        self.launch_btn.pack(fill=tk.X, pady=(0, 10))

        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ STOP SERVICES",
            font=("Segoe UI", 12),
            bg='#ff4444',
            fg='#ffffff',
            command=self.stop_services,
            state=tk.DISABLED,
            height=1
        )
        self.stop_btn.pack(fill=tk.X, pady=(0, 10))

        # Quick Links
        link_frame = tk.Frame(self, bg='#1a1a2e')
        link_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            link_frame,
            text="📊 Open Dashboard",
            bg='#0f6cbd',
            fg='#ffffff',
            command=self.open_dashboard
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            link_frame,
            text="⚙️ Settings",
            bg='#404060',
            fg='#ffffff',
            command=self.open_settings
        ).pack(side=tk.LEFT, padx=5)

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        self.monitor_thread.start()

    def launch_services(self):
        """Launch backend and frontend"""
        self.launch_btn.config(state=tk.DISABLED)

        # Launch backend
        try:
            venv_python = Path(".venv/Scripts/python.exe")
            self.backend_proc = subprocess.Popen(
                [str(venv_python), "-m", "uvicorn", "python_service.api:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).parent
            )
        except Exception as e:
            self.update_status("backend", False, f"Error: {str(e)[:30]}")
            return

        # Launch frontend
        try:
            self.frontend_proc = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd="web_platform/frontend"
            )
        except Exception as e:
            self.update_status("frontend", False, f"Error: {str(e)[:30]}")
            return

        self.stop_btn.config(state=tk.NORMAL)

    def stop_services(self):
        """Stop all services"""
        if self.backend_proc:
            self.backend_proc.terminate()
            self.backend_proc = None
        if self.frontend_proc:
            self.frontend_proc.terminate()
            self.frontend_proc = None

        self.launch_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def monitor_services(self):
        """Monitor service health in background"""
        while True:
            # Check backend on port 8000
            try:
                requests.get("http://localhost:8000/health", timeout=1)
                self.update_status("backend", True, "Running on port 8000")
            except:
                self.update_status("backend", False, "Not responding")

            # Check frontend on port 3000
            try:
                requests.get("http://localhost:3000", timeout=1)
                self.update_status("frontend", True, "Running on port 3000")
            except:
                self.update_status("frontend", False, "Not responding")

            time.sleep(2)

    def update_status(self, service: str, is_running: bool, message: str):
        """Update service status indicator"""
        color = "#00ff88" if is_running else "#ff4444"

        if service == "backend":
            self.backend_status.itemconfig(self.backend_indicator, fill=color)
            self.backend_status.itemconfig(self.backend_text, text=message)
        else:
            self.frontend_status.itemconfig(self.frontend_indicator, fill=color)
            self.frontend_status.itemconfig(self.frontend_text, text=message)

    def open_dashboard(self):
        """Open frontend in browser"""
        import webbrowser
        webbrowser.open("http://localhost:3000")

    def open_settings(self):
        """Open settings window"""
        # Placeholder
        pass

    def _check_services(self):
        """Check if services are already running"""
        # Implementation
        pass

    def on_closing(self):
        self.stop_services()
        self.destroy()

if __name__ == "__main__":
    app = FortunaLauncher()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()