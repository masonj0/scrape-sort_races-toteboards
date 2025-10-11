#!/usr/bin/env python3
"""
FORTUNA FAUCET - Windows Native Status Monitor
"""

import asyncio
import httpx
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import os
import webbrowser

def load_api_key():
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('API_KEY='):
                    return line.split('=', 1)[1].strip().strip('\"')
    return None

API_BASE_URL = "http://localhost:8000"
API_KEY = load_api_key()

class FortunaStatusMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fortuna Faucet - System Status Monitor")
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        self.geometry("1000x750")
        self.configure(bg='#1a1a2e')

        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.is_running = True
        self.refresh_interval = 30000

        self._setup_styles()
        self._create_widgets()
        self.after(100, self.initial_load)

    def initial_load(self):
        if not API_KEY:
            messagebox.showerror("Config Error", "API_KEY not found in .env file!")
            self.destroy()
            return
        self.schedule_refresh()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TLabel', background='#16213e', foreground='#e94560', font=('Segoe UI', 16, 'bold'), padding=15)
        style.configure('Accent.TButton', background='#e94560', foreground='#ffffff', font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=10)

    def _create_widgets(self):
        # Menu, Header, Controls, Notebook, Status Bar...
        # This is a simplified version for brevity in this format.
        # The full implementation would build the detailed UI.
        self.status_indicator = tk.Label(self, text="● Initializing...", bg='#1a1a2e', fg='#ffcc00', font=('Segoe UI', 10, 'bold'))
        self.status_indicator.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=10)
        self.adapter_tree = ttk.Treeview(self, columns=('Adapter', 'Status', 'Races', 'Duration', 'Error'), show='headings')
        for col in self.adapter_tree['columns']:
            self.adapter_tree.heading(col, text=col)
        self.adapter_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    async def refresh_data(self):
        try:
            headers = {"X-API-Key": API_KEY}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{API_BASE_URL}/api/adapters/status", headers=headers)
                response.raise_for_status()
                adapters = response.json()
            self.update_adapter_display(adapters)
            self.status_indicator.config(text="● All Systems Operational", fg='#00ff88')
        except httpx.ConnectError:
            self.status_indicator.config(text="● Backend Offline", fg='#ff4444')
            self.update_adapter_display([{"error": "Cannot connect to backend."}])
        except Exception as e:
            self.status_indicator.config(text=f"● Error: {e}", fg='#ff4444')
            self.update_adapter_display([{"error": str(e)}])

    def update_adapter_display(self, adapters):
        for item in self.adapter_tree.get_children():
            self.adapter_tree.delete(item)
        if adapters and "error" not in adapters[0]:
            for adapter in adapters:
                status = adapter.get('status', 'UNKNOWN')
                tag = 'success' if status == 'SUCCESS' else 'error'
                self.adapter_tree.insert('', tk.END, values=(adapter.get('name', 'Unknown'), status, adapter.get('races_fetched', 0), f"{adapter.get('fetch_duration', 0):.2f}", adapter.get('error_message', '—')[:60]), tags=(tag,))
        else:
            self.adapter_tree.insert('', tk.END, values=('SYSTEM ERROR', 'FAILED', 0, 0, adapters[0].get('error', 'Unknown')[:60]), tags=('error',))
        self.adapter_tree.tag_configure('success', foreground='#00ff88')
        self.adapter_tree.tag_configure('error', foreground='#ff4444')

    def schedule_refresh(self):
        if self.is_running and self.auto_refresh_var.get():
            asyncio.run(self.refresh_data())
        if self.is_running:
            self.after(self.refresh_interval, self.schedule_refresh)

    def on_closing(self):
        self.is_running = False
        self.destroy()

if __name__ == "__main__":
    app = FortunaStatusMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
