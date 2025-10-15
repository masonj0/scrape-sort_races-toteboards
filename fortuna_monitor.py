# fortuna_monitor.py - Windows-Optimized Version

import asyncio
import httpx
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from collections import deque
import threading
import psutil
import sys
import time

# Try to import matplotlib for graphs
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    GRAPHS_AVAILABLE = True
except ImportError:
    GRAPHS_AVAILABLE = False

API_BASE_URL = "http://localhost:8000"

class PerformanceTracker:
    def __init__(self, max_history=100):
        self.timestamps = deque(maxlen=max_history)
        self.race_counts = deque(maxlen=max_history)
        self.fetch_durations = deque(maxlen=max_history)
        self.success_rates = deque(maxlen=max_history)
        self.cpu_usage = deque(maxlen=max_history)
        self.memory_usage = deque(maxlen=max_history)

    def add_datapoint(self, races, duration, success_rate):
        self.timestamps.append(datetime.now())
        self.race_counts.append(races)
        self.fetch_durations.append(duration)
        self.success_rates.append(success_rate)
        self.cpu_usage.append(psutil.cpu_percent(interval=None))
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024) # MB

    def export_to_csv(self, filename):
        import csv
        history = self.get_history()
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Races', 'Duration', 'Success Rate', 'CPU %', 'Memory MB'])
            for i in range(len(history['times'])):
                writer.writerow([
                    history['times'][i].isoformat(),
                    history['races'][i],
                    history['durations'][i],
                    history['success'][i],
                    history['cpu'][i],
                    history['memory'][i]
                ])

    def get_history(self):
        return {
            'times': list(self.timestamps),
            'races': list(self.race_counts),
            'durations': list(self.fetch_durations),
            'success': list(self.success_rates),
            'cpu': list(self.cpu_usage),
            'memory': list(self.memory_usage)
        }

class FortunaAdvancedMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fortuna Faucet - Advanced Monitor")
        self.geometry("900x650")
        self.api_key = os.getenv("API_KEY")
        self.performance = PerformanceTracker()
        self.running = True
        self._create_widgets()
        self.after(100, self.start_fetch_thread)

    def _create_widgets(self):
        self._create_control_panel()
        # ... (rest of the widget creation)

    def _create_control_panel(self):
        control_frame = tk.Frame(self, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(
            control_frame,
            text="📊 Export Performance Data",
            command=self.export_data,
            bg='#0f3460',
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            control_frame,
            text="💻 System Info",
            command=self.show_system_info,
            bg='#0f3460',
            fg='#ffffff',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=5)

    def start_fetch_thread(self):
        self.fetch_thread = threading.Thread(target=self._fetch_data_loop, daemon=True)
        self.fetch_thread.start()

    def _fetch_data_loop(self):
        while self.running:
            try:
                # Use httpx for async requests
                with httpx.Client(headers={"X-API-KEY": self.api_key}, timeout=5) as client:
                    response = client.get(f"{API_BASE_URL}/api/adapters/status")
                if response.status_code == 200:
                    data = response.json()
                    # Add performance datapoint
                    total_races = sum(a.get('races_fetched', 0) for a in data)
                    successful_adapters = [a for a in data if a.get('status') == 'SUCCESS']
                    success_rate = (len(successful_adapters) / len(data) * 100) if data else 0
                    avg_duration = sum(a.get('fetch_duration', 0) for a in successful_adapters) / len(successful_adapters) if successful_adapters else 0
                    self.performance.add_datapoint(total_races, avg_duration, success_rate)

                    self.after(0, self.update_ui, data)
            except httpx.RequestError:
                pass
            time.sleep(10) # Refresh interval

    def update_ui(self, data):
        # This is where you would update the tkinter UI with the new data
        # For example, you might update a treeview or a graph
        pass

    def export_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"fortuna_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if filename:
            try:
                self.performance.export_to_csv(filename)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def show_system_info(self):
        vm = psutil.virtual_memory()
        info = f"""
System Information:

CPU Usage: {psutil.cpu_percent(interval=1)}%
CPU Cores: {psutil.cpu_count()}
Memory Total: {vm.total / 1024 / 1024 / 1024:.2f} GB
Memory Available: {vm.available / 1024 / 1024 / 1024:.2f} GB
Memory Used: {vm.percent}%

Disk Usage: {psutil.disk_usage('/').percent}%
Python Version: {sys.version.split()[0]}
"""
        messagebox.showinfo("System Information", info)

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == '__main__':
    # Load .env variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: dotenv is not installed. Script assumes environment variables are set.")
    app = FortunaAdvancedMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()