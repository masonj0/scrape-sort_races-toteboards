# launcher_gui.py - The single, graphical entry point for Fortuna Faucet.
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import threading
import time
import requests
import os
import psutil

# --- Configuration ---
BACKEND_PORT = 8000
FRONTEND_PORT = 3000

class FortunaLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐴 Fortuna Faucet - System Control")
        self.geometry("450x350")
        self.configure(bg='#1a1a2e')
        self.resizable(False, False)

        self.backend_proc = None
        self.frontend_proc = None
        self.is_running = False

        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.monitor_thread = threading.Thread(target=self._monitor_services_loop, daemon=True)
        self.monitor_thread.start()

    def _create_widgets(self):
        style = ttk.Style(self)
        style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Segoe UI', 12))

        ttk.Label(self, text="Fortuna Faucet Control Panel", font=('Segoe UI', 16, 'bold')).pack(pady=20)

        self.backend_status = ttk.Label(self, text="● Backend: OFFLINE", foreground="#F44336")
        self.backend_status.pack(pady=5)

        self.frontend_status = ttk.Label(self, text="● Frontend: OFFLINE", foreground="#F44336")
        self.frontend_status.pack(pady=5)

        self.action_button = tk.Button(
            self, text="▶ START SERVICES", font=("Segoe UI", 14, "bold"),
            bg="#4CAF50", fg="white", relief=tk.FLAT, width=25, command=self.toggle_services)
        self.action_button.pack(pady=30)

        self.status_log = tk.Label(self, text="Ready to start.", bg='#1a1a2e', fg='#B0B0B0', font=('Segoe UI', 9))
        self.status_log.pack(side=tk.BOTTOM, pady=10)

    def toggle_services(self):
        if self.is_running:
            self._stop_services()
        else:
            self._start_services()

    def _start_services(self):
        self.action_button.config(state=tk.DISABLED, text="STARTING...")
        self.status_log.config(text="Attempting to launch services...")
        self.is_running = True # Set intent to run

        # Use CREATE_NO_WINDOW to hide console windows on Windows
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        # Start Backend
        self.backend_status.config(text="● Backend: STARTING...", foreground="#FFC107")
        backend_command = ["cmd", "/c", "call .venv\\Scripts\\activate.bat && uvicorn python_service.api:app --host 127.0.0.1 --port 8000"]
        self.backend_proc = subprocess.Popen(backend_command, creationflags=creation_flags)

        # Start Frontend
        self.frontend_status.config(text="● Frontend: STARTING...", foreground="#FFC107")
        frontend_command = ["cmd", "/c", "cd web_platform/frontend && npm run dev"]
        self.frontend_proc = subprocess.Popen(frontend_command, creationflags=creation_flags)

        self.status_log.config(text="Services launched. Waiting for health checks...")

    def _stop_services(self):
        self.action_button.config(state=tk.DISABLED, text="STOPPING...")
        self.status_log.config(text="Attempting to stop all services...")
        self.is_running = False # Set intent to stop

        for proc in [self.backend_proc, self.frontend_proc]:
            if proc and proc.poll() is None:
                try:
                    # Kill the entire process tree to shut down children (like node)
                    parent = psutil.Process(proc.pid)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                except psutil.NoSuchProcess:
                    pass # Process already gone

        self.backend_proc = None
        self.frontend_proc = None
        self.status_log.config(text="Services stopped.")

    def _monitor_services_loop(self):
        while True:
            backend_ok, frontend_ok = False, False
            try:
                # Check Backend
                if self.backend_proc and self.backend_proc.poll() is None:
                    try:
                        r = requests.get(f"http://localhost:{BACKEND_PORT}/health", timeout=1)
                        if r.status_code == 200:
                            backend_ok = True
                    except requests.RequestException:
                        pass

                # Check Frontend
                if self.frontend_proc and self.frontend_proc.poll() is None:
                    try:
                        r = requests.get(f"http://localhost:{FRONTEND_PORT}", timeout=1)
                        if r.status_code == 200:
                            frontend_ok = True
                    except requests.RequestException:
                        pass

                # If we intend to be running but a process has died, set state to not running
                if self.is_running and (not backend_ok or not frontend_ok):
                    if (self.backend_proc and self.backend_proc.poll() is not None) or \
                       (self.frontend_proc and self.frontend_proc.poll() is not None):
                        self.is_running = False # A service has crashed

            finally:
                # Schedule UI update on the main thread
                self.after(0, self._update_ui, backend_ok, frontend_ok)

            time.sleep(3) # Check every 3 seconds

    def _update_ui(self, backend_ok, frontend_ok):
        # Update Backend Status
        if backend_ok:
            self.backend_status.config(text="● Backend: ONLINE", foreground="#4CAF50")
        elif self.is_running and self.backend_proc:
            self.backend_status.config(text="● Backend: STARTING...", foreground="#FFC107")
        else:
            self.backend_status.config(text="● Backend: OFFLINE", foreground="#F44336")

        # Update Frontend Status
        if frontend_ok:
            self.frontend_status.config(text="● Frontend: ONLINE", foreground="#4CAF50")
        elif self.is_running and self.frontend_proc:
            self.frontend_status.config(text="● Frontend: STARTING...", foreground="#FFC107")
        else:
            self.frontend_status.config(text="● Frontend: OFFLINE", foreground="#F44336")

        # Update Button State
        if self.is_running:
            self.action_button.config(text="■ STOP SERVICES", bg="#F44336")
            if backend_ok and frontend_ok:
                self.action_button.config(state=tk.NORMAL)
                self.status_log.config(text="All services are online and healthy.")
        else:
            self.action_button.config(text="▶ START SERVICES", bg="#4CAF50", state=tk.NORMAL)
            self.status_log.config(text="Ready to start.")

    def _on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Services are running. Do you want to stop them and exit?"):
                self._stop_services()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    # Pre-flight check for .venv
    if not os.path.exists('.venv'):
        messagebox.showerror("Error", "Python virtual environment not found. Please run INSTALL_FORTUNA.bat first.")
    else:
        app = FortunaLauncher()
        app.mainloop()