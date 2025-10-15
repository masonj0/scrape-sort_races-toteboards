#!/usr/bin/env python3
"""
FORTUNA FAUCET - Enhanced Windows Monitor with Race Management
"""

import asyncio
import httpx
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Any, Optional
import os
import time
import requests
import threading
import webbrowser

# Try to import matplotlib for graphs
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

class FortunaEnhancedMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fortuna Faucet - Data Management Console")

        # DPI Awareness
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.geometry("1400x900")
        self.configure(bg='#1a1a2e')

        self.is_running = True
        self.refresh_interval = 30000
        self.auto_refresh_var = tk.BooleanVar(value=True)

        # Data state
        self.current_races = []
        self.filtered_races = []
        self.selected_analyzer = "trifecta"

        # Filter state
        self.filter_min_score = tk.IntVar(value=0)
        self.filter_max_field = tk.IntVar(value=20)
        self.filter_source = tk.StringVar(value="All")
        self.filter_qualified_only = tk.BooleanVar(value=False)

        self._setup_styles()
        self._create_widgets()
        self.after(100, self.initial_load)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Header styles
        style.configure('Header.TLabel',
                       background='#16213e',
                       foreground='#e94560',
                       font=('Segoe UI', 16, 'bold'),
                       padding=10)

        # Button styles
        style.configure('Action.TButton',
                       background='#e94560',
                       foreground='#ffffff',
                       font=('Segoe UI', 10, 'bold'),
                       padding=8)

    def _create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        ttk.Label(header_frame,
                 text="🏇 FORTUNA FAUCET - Data Management Console",
                 style='Header.TLabel').pack(pady=15)

        # Main container with 3-panel layout
        main_container = tk.PanedWindow(self,
                                        orient=tk.HORIZONTAL,
                                        bg='#1a1a2e',
                                        sashwidth=3,
                                        sashrelief=tk.RAISED)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEFT PANEL: Control & Filter
        self.left_panel = self._create_left_panel(main_container)
        main_container.add(self.left_panel, minsize=300)

        # CENTER PANEL: Race List
        self.center_panel = self._create_center_panel(main_container)
        main_container.add(self.center_panel, minsize=600)

        # RIGHT PANEL: Race Details
        self.right_panel = self._create_right_panel(main_container)
        main_container.add(self.right_panel, minsize=350)

        # Status bar at bottom
        self._create_status_bar()

    def _create_left_panel(self, parent):
        """Control panel with fetch controls and filters."""
        panel = tk.Frame(parent, bg='#0f3460', padx=10, pady=10)

        # === FETCH CONTROLS ===
        fetch_frame = tk.LabelFrame(panel,
                                    text="📡 Data Fetching",
                                    bg='#0f3460',
                                    fg='#ffffff',
                                    font=('Segoe UI', 11, 'bold'),
                                    padx=10,
                                    pady=10)
        fetch_frame.pack(fill=tk.X, pady=(0, 15))

        analyzer_combo = ttk.Combobox(fetch_frame,
                                      values=['trifecta'],
                                      state='readonly',
                                      width=25)
        analyzer_combo.set('trifecta')
        analyzer_combo.pack(fill=tk.X, pady=(2, 10))
        analyzer_combo.bind('<<ComboboxSelected>>',
                           lambda e: self.on_analyzer_changed(analyzer_combo.get()))

        fetch_btn = tk.Button(fetch_frame,
                             text="🔄 Fetch Qualified Races",
                             command=self.manual_fetch,
                             bg='#e94560',
                             fg='#ffffff',
                             font=('Segoe UI', 10, 'bold'),
                             relief=tk.FLAT,
                             padx=15,
                             pady=8,
                             cursor='hand2')
        fetch_btn.pack(fill=tk.X, pady=(0, 8))

        auto_refresh_cb = tk.Checkbutton(fetch_frame,
                                         text="Auto-refresh (30s)",
                                         variable=self.auto_refresh_var,
                                         bg='#0f3460',
                                         fg='#ffffff',
                                         selectcolor='#16213e',
                                         font=('Segoe UI', 9))
        auto_refresh_cb.pack(anchor=tk.W)

        # === FILTER CONTROLS ===
        filter_frame = tk.LabelFrame(panel,
                                     text="🔍 Filters",
                                     bg='#0f3460',
                                     fg='#ffffff',
                                     font=('Segoe UI', 11, 'bold'),
                                     padx=10,
                                     pady=10)
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(filter_frame,
                text=f"Min Score: {self.filter_min_score.get()}",
                bg='#0f3460',
                fg='#ffffff',
                font=('Segoe UI', 9)).pack(anchor=tk.W)

        score_scale = tk.Scale(filter_frame,
                              from_=0,
                              to=100,
                              orient=tk.HORIZONTAL,
                              variable=self.filter_min_score,
                              command=self.on_filter_changed,
                              bg='#0f3460',
                              fg='#ffffff',
                              highlightthickness=0,
                              troughcolor='#16213e')
        score_scale.pack(fill=tk.X, pady=(2, 10))

        tk.Label(filter_frame,
                text=f"Max Field Size: {self.filter_max_field.get()}",
                bg='#0f3460',
                fg='#ffffff',
                font=('Segoe UI', 9)).pack(anchor=tk.W)

        field_scale = tk.Scale(filter_frame,
                              from_=2,
                              to=20,
                              orient=tk.HORIZONTAL,
                              variable=self.filter_max_field,
                              command=self.on_filter_changed,
                              bg='#0f3460',
                              fg='#ffffff',
                              highlightthickness=0,
                              troughcolor='#16213e')
        field_scale.pack(fill=tk.X, pady=(2, 10))

        source_combo = ttk.Combobox(filter_frame,
                                    textvariable=self.filter_source,
                                    values=['All', 'TVG', 'BetfairExchange', 'AtTheRaces', 'SportingLife'],
                                    state='readonly',
                                    width=25)
        source_combo.pack(fill=tk.X, pady=(2, 10))
        source_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        qualified_cb = tk.Checkbutton(filter_frame,
                                     text="Qualified Only",
                                     variable=self.filter_qualified_only,
                                     command=self.apply_filters,
                                     bg='#0f3460',
                                     fg='#ffffff',
                                     selectcolor='#16213e',
                                     font=('Segoe UI', 9))
        qualified_cb.pack(anchor=tk.W, pady=(0, 5))

        clear_btn = tk.Button(filter_frame,
                             text="Clear Filters",
                             command=self.clear_filters,
                             bg='#16213e',
                             fg='#ffffff',
                             relief=tk.FLAT,
                             padx=10,
                             pady=5)
        clear_btn.pack(fill=tk.X)

        # === STATISTICS ===
        stats_frame = tk.LabelFrame(panel,
                                   text="📊 Statistics",
                                   bg='#0f3460',
                                   fg='#ffffff',
                                   font=('Segoe UI', 11, 'bold'),
                                   padx=10,
                                   pady=10)
        stats_frame.pack(fill=tk.X)

        self.stats_text = tk.Text(stats_frame,
                                 height=8,
                                 bg='#16213e',
                                 fg='#ffffff',
                                 font=('Courier New', 9),
                                 relief=tk.FLAT,
                                 state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        return panel

    def _create_center_panel(self, parent):
        """Race list with sortable columns."""
        panel = tk.Frame(parent, bg='#0f3460', padx=10, pady=10)

        header = tk.Frame(panel, bg='#0f3460')
        header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(header,
                text="Race Results",
                bg='#0f3460',
                fg='#ffffff',
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        self.race_count_label = tk.Label(header,
                                         text="0 races",
                                         bg='#0f3460',
                                         fg='#00ff88',
                                         font=('Segoe UI', 10))
        self.race_count_label.pack(side=tk.RIGHT)

        tree_frame = tk.Frame(panel, bg='#0f3460')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ('venue', 'race_num', 'time', 'score', 'field', 'source', 'qualified')
        self.race_tree = ttk.Treeview(tree_frame,
                                      columns=columns,
                                      show='headings',
                                      yscrollcommand=vsb.set,
                                      xscrollcommand=hsb.set,
                                      selectmode='browse')

        self.race_tree.heading('venue', text='Venue', command=lambda: self.sort_column('venue'))
        self.race_tree.heading('race_num', text='Race #', command=lambda: self.sort_column('race_num'))
        self.race_tree.heading('time', text='Post Time', command=lambda: self.sort_column('time'))
        self.race_tree.heading('score', text='Score', command=lambda: self.sort_column('score'))
        self.race_tree.heading('field', text='Field', command=lambda: self.sort_column('field'))
        self.race_tree.heading('source', text='Source', command=lambda: self.sort_column('source'))
        self.race_tree.heading('qualified', text='Qualified', command=lambda: self.sort_column('qualified'))

        self.race_tree.column('venue', width=150)
        self.race_tree.column('race_num', width=60, anchor=tk.CENTER)
        self.race_tree.column('time', width=120)
        self.race_tree.column('score', width=70, anchor=tk.CENTER)
        self.race_tree.column('field', width=60, anchor=tk.CENTER)
        self.race_tree.column('source', width=120)
        self.race_tree.column('qualified', width=80, anchor=tk.CENTER)

        self.race_tree.bind('<<TreeviewSelect>>', self.on_race_selected)

        vsb.config(command=self.race_tree.yview)
        hsb.config(command=self.race_tree.xview)

        self.race_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        return panel

    def _create_right_panel(self, parent):
        """Race details and runner information."""
        panel = tk.Frame(parent, bg='#0f3460', padx=10, pady=10)

        self.detail_header = tk.Label(panel,
                                      text="Select a race to view details",
                                      bg='#0f3460',
                                      fg='#ffffff',
                                      font=('Segoe UI', 11, 'bold'))
        self.detail_header.pack(pady=(0, 10))

        info_frame = tk.LabelFrame(panel,
                                  text="Race Information",
                                  bg='#0f3460',
                                  fg='#ffffff',
                                  font=('Segoe UI', 10, 'bold'),
                                  padx=10,
                                  pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.race_info_text = tk.Text(info_frame,
                                     height=6,
                                     bg='#16213e',
                                     fg='#ffffff',
                                     font=('Courier New', 9),
                                     relief=tk.FLAT,
                                     state=tk.DISABLED)
        self.race_info_text.pack(fill=tk.BOTH, expand=True)

        runners_frame = tk.LabelFrame(panel,
                                     text="Runners & Odds",
                                     bg='#0f3460',
                                     fg='#ffffff',
                                     font=('Segoe UI', 10, 'bold'),
                                     padx=10,
                                     pady=10)
        runners_frame.pack(fill=tk.BOTH, expand=True)

        runner_vsb = ttk.Scrollbar(runners_frame, orient="vertical")

        runner_columns = ('num', 'name', 'odds')
        self.runner_tree = ttk.Treeview(runners_frame,
                                       columns=runner_columns,
                                       show='headings',
                                       yscrollcommand=runner_vsb.set,
                                       height=15)

        self.runner_tree.heading('num', text='#')
        self.runner_tree.heading('name', text='Horse Name')
        self.runner_tree.heading('odds', text='Best Odds')

        self.runner_tree.column('num', width=40, anchor=tk.CENTER)
        self.runner_tree.column('name', width=180)
        self.runner_tree.column('odds', width=80, anchor=tk.CENTER)

        runner_vsb.config(command=self.runner_tree.yview)

        self.runner_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        runner_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        return panel

    def _create_status_bar(self):
        """Status bar with connection status and last update time."""
        status_frame = tk.Frame(self, bg='#0f3460', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame,
                                     text="● Ready",
                                     bg='#0f3460',
                                     fg='#00ff88',
                                     font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=15)

        self.last_update_label = tk.Label(status_frame,
                                         text="Last Update: Never",
                                         bg='#0f3460',
                                         fg='#ffffff',
                                         font=('Segoe UI', 9))
        self.last_update_label.pack(side=tk.RIGHT, padx=15)

    def initial_load(self):
        """Initial data load on startup."""
        if not API_KEY:
            messagebox.showerror("Configuration Error",
                               "API_KEY not found in .env file!\\n\\n"
                               "Please configure your API key and restart.")
            self.destroy()
            return

        self.manual_fetch()
        self.schedule_refresh()

    def manual_fetch(self):
        """Manually trigger a data fetch."""
        self.status_label.config(text="● Fetching...", fg='#ffcc00')
        self.update()
        threading.Thread(target=lambda: asyncio.run(self.fetch_races())).start()

    async def fetch_races(self):
        """Fetch qualified races from the API."""
        try:
            headers = {"X-API-Key": API_KEY}
            today = datetime.now().strftime('%Y-%m-%d')

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/races/qualified/{self.selected_analyzer}",
                    headers=headers,
                    params={"race_date": today}
                )
                response.raise_for_status()
                data = response.json()

            self.current_races = data.get('races', [])
            self.update_ui_after_fetch()

        except httpx.ConnectError:
            self.show_error("Backend Offline", "Cannot connect to Fortuna backend.")
        except Exception as e:
            self.show_error("Fetch Error", str(e))

    def update_ui_after_fetch(self):
        """Update UI after successful fetch."""
        self.status_label.config(text="● Connected", fg='#00ff88')
        self.last_update_label.config(
            text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
        )
        self.apply_filters()
        self.update_statistics()

    def apply_filters(self):
        """Apply current filters to race list."""
        self.filtered_races = []

        for race in self.current_races:
            score = race.get('qualification_score', 0) or 0
            if score < self.filter_min_score.get():
                continue

            active_runners = [r for r in race.get('runners', []) if not r.get('scratched', False)]
            if len(active_runners) > self.filter_max_field.get():
                continue

            if self.filter_source.get() != 'All':
                if race.get('source') != self.filter_source.get():
                    continue

            if self.filter_qualified_only.get():
                if not (score > 0):
                    continue

            self.filtered_races.append(race)

        self.update_race_tree()

    def update_race_tree(self):
        """Update the race treeview with filtered results."""
        for item in self.race_tree.get_children():
            self.race_tree.delete(item)

        for race in self.filtered_races:
            active_runners = [r for r in race.get('runners', []) if not r.get('scratched', False)]
            score = race.get('qualification_score', 0) or 0

            post_time = race.get('start_time', '')
            if post_time:
                try:
                    dt = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
                    post_time = dt.strftime('%H:%M')
                except:
                    pass

            qualified = "✓" if score > 0 else ""

            values = (
                race.get('venue', 'Unknown'),
                race.get('race_number', '?'),
                post_time,
                f"{score:.1f}" if score > 0 else "--",
                len(active_runners),
                race.get('source', 'Unknown'),
                qualified
            )

            item_id = self.race_tree.insert('', tk.END, values=values)
            self.race_tree.item(item_id, tags=(race.get('id', ''),))

        self.race_count_label.config(
            text=f"{len(self.filtered_races)} of {len(self.current_races)} races"
        )

    def on_race_selected(self, event):
        """Handle race selection in treeview."""
        selection = self.race_tree.selection()
        if not selection:
            return

        item = selection[0]
        tags = self.race_tree.item(item, 'tags')
        if not tags:
            return

        race_id = tags[0]

        race = next((r for r in self.filtered_races if r.get('id') == race_id), None)
        if not race:
            return

        self.display_race_details(race)

    def display_race_details(self, race):
        """Display detailed information for selected race."""
        self.detail_header.config(
            text=f"{race.get('venue', 'Unknown')} - Race {race.get('race_number', '?')}"
        )

        self.race_info_text.config(state=tk.NORMAL)
        self.race_info_text.delete('1.0', tk.END)

        info_lines = [
            f"ID:           {race.get('id', 'N/A')}",
            f"Source:       {race.get('source', 'Unknown')}",
            f"Post Time:    {race.get('start_time', 'N/A')}",
            f"Score:        {race.get('qualification_score', 0):.2f}",
            f"Distance:     {race.get('distance', 'N/A')}",
            f"Surface:      {race.get('surface', 'N/A')}"
        ]

        self.race_info_text.insert('1.0', '\n'.join(info_lines))
        self.race_info_text.config(state=tk.DISABLED)

        for item in self.runner_tree.get_children():
            self.runner_tree.delete(item)

        runners = race.get('runners', [])
        runners_with_odds = [(r, self.get_best_odds(r)) for r in runners if not r.get('scratched', False)]
        runners_with_odds.sort(key=lambda x: x[1] if x[1] is not None else 999)

        for runner, best_odds in runners_with_odds:
            odds_str = f"{best_odds:.2f}" if best_odds else "--"
            self.runner_tree.insert('', tk.END, values=(
                runner.get('number', '?'),
                runner.get('name', 'Unknown'),
                odds_str
            ))

    def get_best_odds(self, runner):
        """Get best odds from all sources for a runner."""
        odds_dict = runner.get('odds', {})
        if not odds_dict:
            return None

        valid_odds = []
        for source, odds_data in odds_dict.items():
            if isinstance(odds_data, dict):
                win_odds = odds_data.get('win')
                if win_odds and win_odds < 999:
                    valid_odds.append(win_odds)

        return min(valid_odds) if valid_odds else None

    def update_statistics(self):
        """Update statistics panel."""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete('1.0', tk.END)

        total = len(self.current_races)
        qualified = sum(1 for r in self.current_races if (r.get('qualification_score', 0) or 0) > 0)

        if total > 0:
            avg_score = sum((r.get('qualification_score', 0) or 0) for r in self.current_races) / total

            sources = {}
            for race in self.current_races:
                source = race.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1

            stats = [
                f"Total Races:     {total}",
                f"Qualified:       {qualified} ({qualified/total*100:.1f}%)",
                f"Avg Score:       {avg_score:.2f}",
                f"",
                "By Source:"
            ]

            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {source:15} {count:3}")

            self.stats_text.insert('1.0', '\n'.join(stats))
        else:
            self.stats_text.insert('1.0', "No data available.\\n\\nClick 'Fetch Qualified Races'\\nto load data.")

        self.stats_text.config(state=tk.DISABLED)

    def on_filter_changed(self, value):
        """Handle filter slider changes."""
        for child in self.left_panel.winfo_children():
            if isinstance(child, tk.LabelFrame) and child.cget('text') == '🔍 Filters':
                for widget in child.winfo_children():
                    if isinstance(widget, tk.Label):
                        if 'Min Score' in widget.cget('text'):
                            widget.config(text=f"Min Score: {self.filter_min_score.get()})")
                        elif 'Max Field' in widget.cget('text'):
                            widget.config(text=f"Max Field Size: {self.filter_max_field.get()})")

        self.apply_filters()

    def on_analyzer_changed(self, analyzer):
        """Handle analyzer selection change."""
        self.selected_analyzer = analyzer

    def clear_filters(self):
        """Reset all filters to default values."""
        self.filter_min_score.set(0)
        self.filter_max_field.set(20)
        self.filter_source.set('All')
        self.filter_qualified_only.set(False)
        self.apply_filters()

    def sort_column(self, col, reverse=False):
        """Sort treeview by column."""
        pass

    def schedule_refresh(self):
        """Schedule the next data refresh."""
        if self.is_running and self.auto_refresh_var.get():
            self.after(self.refresh_interval, self.manual_fetch)

    def show_error(self, title, message):
        """Show error message in status bar."""
        self.status_label.config(text=f"● Error: {title}", fg='#e94560')
        self.last_update_label.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        messagebox.showerror(title, message)

    def on_closing(self):
        """Handle window closing."""
        self.is_running = False
        self.destroy()

if __name__ == '__main__':
    if not API_KEY:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", "API_KEY not found in .env file.")
    else:
        app = FortunaEnhancedMonitor()
        app.mainloop()
