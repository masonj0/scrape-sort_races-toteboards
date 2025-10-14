# fortuna_monitor.py
# A professional, real-time GUI command deck for monitoring the Fortuna Faucet system.

import os
import time
import requests
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import collections

# Matplotlib imports for graphing
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 10  # seconds
HISTORY_LENGTH = 30 # Number of data points to keep for graphs

class FortunaAdvancedMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fortuna Faucet - Advanced Monitor")
        self.geometry("900x600")
        self.api_key = os.getenv("API_KEY")

        # Data storage
        self.history = collections.deque(maxlen=HISTORY_LENGTH)

        # --- Style Configuration ---
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(".", background="#2E2E2E", foreground="#E0E0E0", fieldbackground="#3C3C3C")
        style.configure("TNotebook", background="#2E2E2E", borderwidth=0)
        style.configure("TNotebook.Tab", background="#3C3C3C", foreground="#B0B0B0", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#505050")], foreground=[("selected", "#FFFFFF")])
        style.configure("Treeview", rowheight=25, fieldbackground="#3C3C3C", foreground="#E0E0E0")
        style.configure("Treeview.Heading", background="#505050", foreground="#FFFFFF", font=("Segoe UI", 10, 'bold'))
        style.map("Treeview", background=[('selected', '#0078D7')])

        # --- Main Layout ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self._create_live_status_tab()
        self._create_performance_tab()

        if not self.api_key:
            self.show_error("API_KEY not found in environment variables. Please check your .env file.")
            return

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.running = True
        self.thread = threading.Thread(target=self._fetch_data_loop, daemon=True)
        self.thread.start()

    def _create_live_status_tab(self):
        live_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(live_tab, text='Live Status')

        # Stat cards
        stats_frame = ttk.Frame(live_tab)
        stats_frame.pack(fill='x', pady=5)
        self.stat_races = self._create_stat_card(stats_frame, "Total Races", "0")
        self.stat_success = self._create_stat_card(stats_frame, "Success Rate", "0%")
        self.stat_duration = self._create_stat_card(stats_frame, "Avg. Duration", "0s")

        # Adapter Treeview
        tree_frame = ttk.Frame(live_tab)
        tree_frame.pack(expand=True, fill='both')
        self.tree = ttk.Treeview(tree_frame, columns=("Adapter", "Status", "Races", "Duration"), show='headings')
        self.tree.heading("Adapter", text="Adapter", command=lambda: self._sort_treeview("Adapter", False))
        self.tree.heading("Status", text="Status", command=lambda: self._sort_treeview("Status", False))
        self.tree.heading("Races", text="Races Fetched", command=lambda: self._sort_treeview("Races", True))
        self.tree.heading("Duration", text="Duration (s)", command=lambda: self._sort_treeview("Duration", True))
        self.tree.column("Status", width=100, anchor='center')
        self.tree.column("Races", width=120, anchor='e')
        self.tree.column("Duration", width=120, anchor='e')
        self.tree.tag_configure('success', foreground='#4CAF50')
        self.tree.tag_configure('failure', foreground='#F44336')
        self.tree.pack(expand=True, fill='both')

    def _create_performance_tab(self):
        perf_tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(perf_tab, text='Performance')

        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor='#2E2E2E')
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.fig.tight_layout(pad=3.0)

        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#3C3C3C')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('#3C3C3C')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('#3C3C3C')

        self.canvas = FigureCanvasTkAgg(self.fig, master=perf_tab)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _create_stat_card(self, parent, title, value):
        card = tk.LabelFrame(parent, text=title, bg="#3C3C3C", fg="#B0B0B0", font=("Segoe UI", 10))
        card.pack(side='left', expand=True, fill='x', padx=5)
        label = tk.Label(card, text=value, bg="#3C3C3C", fg="#FFFFFF", font=("Segoe UI", 18, 'bold'))
        label.pack(pady=10)
        return label

    def _fetch_data_loop(self):
        while self.running:
            try:
                response = requests.get(f"{API_BASE_URL}/api/adapters/status", headers={"X-API-KEY": self.api_key}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.history.append({'time': datetime.now(), 'data': data})
                    self.after(0, self.update_ui)
            except requests.exceptions.RequestException:
                pass # UI will reflect the offline status via history
            time.sleep(REFRESH_INTERVAL)

    def update_ui(self):
        if not self.history:
            return
        latest_snapshot = self.history[-1]
        data = latest_snapshot['data']
        self._update_stat_cards(data)
        self._update_adapter_treeview(data)
        self._update_performance_graphs()

    def _update_stat_cards(self, data):
        total_races = sum(a.get('races_fetched', 0) for a in data)
        successful_adapters = [a for a in data if a.get('status') == 'SUCCESS']
        success_rate = (len(successful_adapters) / len(data) * 100) if data else 0
        avg_duration = np.mean([a.get('fetch_duration', 0) for a in successful_adapters]) if successful_adapters else 0
        self.stat_races.config(text=f"{total_races}")
        self.stat_success.config(text=f"{success_rate:.1f}%")
        self.stat_duration.config(text=f"{avg_duration:.2f}s")

    def _update_adapter_treeview(self, data):
        self.tree.delete(*self.tree.get_children())
        for adapter in sorted(data, key=lambda x: x.get('name', '')):
            status = adapter.get('status', 'UNKNOWN')
            tag = 'success' if status == 'SUCCESS' else 'failure'
            self.tree.insert('', 'end', values=(
                adapter.get('name'),
                status,
                adapter.get('races_fetched', 0),
                f"{adapter.get('fetch_duration', 0.0):.2f}"
            ), tags=(tag,))

    def _update_performance_graphs(self):
        times = [h['time'] for h in self.history]
        total_races = [sum(a.get('races_fetched', 0) for a in h['data']) for h in self.history]
        success_rates = [(sum(1 for a in h['data'] if a.get('status') == 'SUCCESS') / len(h['data']) * 100) if h['data'] else 0 for h in self.history]
        avg_durations = [np.mean([a.get('fetch_duration', 0) for a in h['data'] if a.get('status') == 'SUCCESS']) if any(a.get('status') == 'SUCCESS' for a in h['data']) else 0 for h in self.history]

        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.clear()

        self.ax1.plot(times, total_races, color='#0078D7', marker='.')
        self.ax1.set_title('Total Races Fetched Over Time', color='white')
        self.ax2.plot(times, success_rates, color='#4CAF50', marker='.')
        self.ax2.set_title('Adapter Success Rate (%) Over Time', color='white')
        self.ax2.set_ylim(0, 105)
        self.ax3.plot(times, avg_durations, color='#FFC107', marker='.')
        self.ax3.set_title('Average Fetch Duration (s) Over Time', color='white')

        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.tick_params(axis='x', rotation=15, labelsize=8)

        self.canvas.draw()

    def _sort_treeview(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            # Try numeric sort first
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            # Fallback to string sort
            data.sort(key=lambda x: x[0], reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda: self._sort_treeview(col, not reverse))

    def show_error(self, message):
        error_label = tk.Label(self, text=message, fg="#F44336", bg="#2E2E2E", font=("Segoe UI", 12))
        error_label.pack(pady=20, padx=20)

    def _on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: dotenv is not installed. Script assumes environment variables are set.")

    app = FortunaAdvancedMonitor()
    app.mainloop()