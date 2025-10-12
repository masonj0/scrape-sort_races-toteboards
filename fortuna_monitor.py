#!/usr/bin/env python3
"""
FORTUNA FAUCET - Advanced Windows Monitor with Performance Graphs
"""

import asyncio
import httpx
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Any
import os
from collections import deque
import threading
import webbrowser

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    GRAPHS_AVAILABLE = True
except ImportError:
    GRAPHS_AVAILABLE = False

def load_api_key():
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('API_KEY='):
                    return line.split('=', 1)[1].strip().strip('\"')
    return None

API_BASE_URL = "http://localhost:8000"
API_KEY = load_api_key()

class PerformanceTracker:
    def __init__(self, max_history=50):
        self.timestamps = deque(maxlen=max_history)
        self.race_counts = deque(maxlen=max_history)
        self.fetch_durations = deque(maxlen=max_history)
        self.success_rates = deque(maxlen=max_history)

    def add_datapoint(self, races, duration, success_rate):
        self.timestamps.append(datetime.now())
        self.race_counts.append(races)
        self.fetch_durations.append(duration)
        self.success_rates.append(success_rate)

class FortunaAdvancedMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fortuna Faucet - Advanced System Monitor")
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        self.geometry("1200x800")
        self.configure(bg='#1a1a2e')

        self.performance = PerformanceTracker()
        self.is_running = True
        self.refresh_interval = 30000
        self.auto_refresh_var = tk.BooleanVar(value=True)

        self._setup_styles()
        self._create_widgets()
        self._setup_keyboard_shortcuts()
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
        style.configure('Header.TLabel', background='#16213e', foreground='#e94560', font=('Segoe UI', 18, 'bold'), padding=15)
        style.configure('Stat.TFrame', background='#0f3460', relief='flat')
        style.configure('StatValue.TLabel', background='#0f3460', foreground='#00ff88', font=('Segoe UI', 24, 'bold'))
        style.configure('StatLabel.TLabel', background='#0f3460', foreground='#ffffff', font=('Segoe UI', 10))

    def _create_widgets(self):
        header_frame = tk.Frame(self, bg='#16213e', height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        ttk.Label(header_frame, text="🎯 FORTUNA FAUCET", style='Header.TLabel').pack(pady=10)

        stats_frame = tk.Frame(self, bg='#1a1a2e')
        stats_frame.pack(fill=tk.X, padx=15, pady=10)
        self._create_stat_card(stats_frame, "Active Adapters", "0", 0)
        self._create_stat_card(stats_frame, "Total Races", "0", 1)
        self._create_stat_card(stats_frame, "Success Rate", "0%", 2)
        self._create_stat_card(stats_frame, "Avg Duration", "0s", 3)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.notebook.add(self._create_adapter_tab(), text="🔧 Adapters")
        if GRAPHS_AVAILABLE:
            self.notebook.add(self._create_graph_tab(), text="📈 Live Performance")

        self._create_control_panel()
        self._create_status_bar()

    def _create_stat_card(self, parent, label, value, column):
        card = ttk.Frame(parent, style='Stat.TFrame', width=250, height=100)
        card.grid(row=0, column=column, padx=5, sticky='ew')
        card.grid_propagate(False)
        parent.grid_columnconfigure(column, weight=1)
        value_label = ttk.Label(card, text=value, style='StatValue.TLabel')
        value_label.pack(pady=(15, 0))
        ttk.Label(card, text=label, style='StatLabel.TLabel').pack()
        setattr(self, f'stat_{label.lower().replace(" ", "_")}', value_label)

    def _create_adapter_tab(self):
        frame = tk.Frame(self.notebook, bg='#0f3460')
        columns = ('Adapter', 'Status', 'Races', 'Duration', 'Error')
        self.adapter_tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            self.adapter_tree.heading(col, text=col)
        self.adapter_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        return frame

    def _create_graph_tab(self):
        frame = tk.Frame(self.notebook, bg='#0f3460')
        if GRAPHS_AVAILABLE:
            self.fig = Figure(figsize=(10, 6), facecolor='#0f3460')
            self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.ax1 = self.fig.add_subplot(2, 2, 1, facecolor='#16213e')
            self.ax2 = self.fig.add_subplot(2, 2, 2, facecolor='#16213e')
            self.ax3 = self.fig.add_subplot(2, 2, 3, facecolor='#16213e')
            self.ax4 = self.fig.add_subplot(2, 2, 4, facecolor='#16213e')
            self.fig.tight_layout(pad=3.0)
        else:
            ttk.Label(frame, text="Install matplotlib to enable graphs: pip install matplotlib").pack(expand=True)
        return frame

    def _create_control_panel(self):
        control_frame = tk.Frame(self, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, padx=15, pady=10)
        tk.Button(control_frame, text="🔄 Refresh Now", command=self.manual_refresh, bg='#e94560', fg='#ffffff', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=25, pady=10).pack(side=tk.LEFT)
        tk.Button(control_frame, text="🌐 Dashboard", command=lambda: webbrowser.open('http://localhost:3000'), bg='#0f3460', fg='#ffffff', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=25, pady=10).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⚙️ Startup", command=self.configure_startup, bg='#0f3460', fg='#ffffff', font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=25, pady=10).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(control_frame, text="Auto-refresh", variable=self.auto_refresh_var, bg='#1a1a2e', fg='#ffffff', selectcolor='#0f3460').pack(side=tk.RIGHT)

    def _create_status_bar(self):
        status_frame = tk.Frame(self, bg='#0f3460', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        self.last_update_label = tk.Label(status_frame, text="Last Update: --:--:--", bg='#0f3460', fg='#ffffff')
        self.last_update_label.pack(side=tk.LEFT, padx=15)
        self.status_indicator = tk.Label(status_frame, text="● Initializing...", bg='#0f3460', fg='#ffcc00')
        self.status_indicator.pack(side=tk.RIGHT, padx=15)

    def manual_refresh(self):
        self.status_indicator.config(text="● Fetching...", fg='#ffcc00')
        self.update()
        threading.Thread(target=lambda: asyncio.run(self.refresh_data())).start()

    async def refresh_data(self):
        try:
            headers = {"X-API-Key": API_KEY}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{API_BASE_URL}/api/adapters/status", headers=headers)
                response.raise_for_status()
                adapters = response.json()
            self.update_ui(adapters)
        except httpx.ConnectError:
            self.update_ui(is_error=True, error_message="Backend Offline")
        except Exception as e:
            self.update_ui(is_error=True, error_message=str(e))

    def update_ui(self, adapters: List[Any] = [], is_error: bool = False, error_message: str = ""):
        if is_error:
            self.status_indicator.config(text=f"● {error_message}", fg='#ff4444')
            for item in self.adapter_tree.get_children(): self.adapter_tree.delete(item)
            self.adapter_tree.insert('', tk.END, values=('SYSTEM ERROR', 'FAILED', 0, 0, error_message[:60]))
            return

        total_races = sum(a.get('races_fetched', 0) for a in adapters)
        avg_duration = sum(a.get('fetch_duration', 0) for a in adapters) / len(adapters) if adapters else 0
        success_rate = sum(1 for a in adapters if a.get('status') == 'SUCCESS') / len(adapters) * 100 if adapters else 0
        self.performance.add_datapoint(total_races, avg_duration, success_rate)

        self.stat_active_adapters.config(text=str(len(adapters)))
        self.stat_total_races.config(text=str(total_races))
        self.stat_success_rate.config(text=f"{success_rate:.1f}%")
        self.stat_avg_duration.config(text=f"{avg_duration:.2f}s")

        for item in self.adapter_tree.get_children(): self.adapter_tree.delete(item)
        for adapter in adapters:
            status = adapter.get('status', 'UNKNOWN')
            self.adapter_tree.insert('', tk.END, values=(adapter.get('name', 'Unknown'), status, adapter.get('races_fetched', 0), f"{adapter.get('fetch_duration', 0):.2f}", adapter.get('error_message', '—')[:60]))

        if GRAPHS_AVAILABLE: self.update_graphs()
        self.last_update_label.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        self.status_indicator.config(text="● All Systems Operational", fg='#00ff88')

    def update_graphs(self):
        history = self.performance
        if not history.timestamps: return
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]: ax.clear()
        self.ax1.plot(history.timestamps, history.race_counts, color='#00ff88')
        self.ax1.set_title('Races Fetched', color='white')
        self.ax2.plot(history.timestamps, history.fetch_durations, color='#e94560')
        self.ax2.set_title('Avg. Fetch Duration (s)', color='white')
        self.ax3.plot(history.timestamps, history.success_rates, color='#ffcc00')
        self.ax3.set_title('Success Rate (%)', color='white')
        self.ax3.set_ylim(0, 105)
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.tick_params(axis='x', labelrotation=30, colors='white')
        self.canvas.draw()

    def schedule_refresh(self):
        if self.is_running and self.auto_refresh_var.get():
            self.manual_refresh()
        if self.is_running:
            self.after(self.refresh_interval, self.schedule_refresh)

    def on_closing(self):
        self.is_running = False
        self.destroy()

if __name__ == "__main__":
    if not API_KEY:
        messagebox.showerror("Config Error", "API_KEY not found in .env file!")
    else:
        app = FortunaAdvancedMonitor()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
\n\n    def _setup_keyboard_shortcuts(self):\n        """Binds standard Windows keyboard shortcuts to core functions."""\n        self.bind('<F5>', lambda e: self.manual_refresh())\n        self.bind('<Control-r>', lambda e: self.manual_refresh())\n        self.bind('<Control-o>', lambda e: webbrowser.open('http://localhost:3000'))\n        self.bind('<Control-q>', lambda e: self.on_closing())\n        self.bind('<Alt-F4>', lambda e: self.on_closing())\n
