# fortuna_status_cli.py
# A real-time, professional CLI dashboard for monitoring the Fortuna Faucet system.

import os
import time
import requests
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 5  # seconds

class LiveStatusDisplay:
    def __init__(self):
        self.console = Console()
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            self.console.print("[bold red]ERROR: API_KEY not found in environment variables. Please check your .env file.[/bold red]")
            exit(1)
        self.headers = {"X-API-KEY": self.api_key}

    def _get_api_data(self, endpoint):
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json(), "[bold green]● ONLINE[/bold green]"
        except requests.exceptions.RequestException as e:
            return None, f"[bold red]● OFFLINE[/bold red] ({type(e).__name__})"

    def generate_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=3),
            Layout(ratio=1, name="main")
        )
        layout["main"].split_row(Layout(name="left"), Layout(name="right", ratio=2))
        layout["left"].split(Layout(name="health"), Layout(name="performance"))

        layout["header"].update(self._generate_header())
        layout["health"].update(self._generate_health_panel())
        layout["performance"].update(self._generate_performance_panel())
        layout["right"].update(self._generate_adapter_panel())
        return layout

    def _generate_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(f"[bold cyan]📊 Fortuna Faucet - Live Status Console[/bold cyan]")
        return Panel(grid, style="blue")

    def _generate_health_panel(self):
        health_data, api_status = self._get_api_data("/health")
        health_table = Table.grid(padding=(0, 1))
        health_table.add_column(style="dim")
        health_table.add_column()
        health_table.add_row("API Status:", api_status)
        health_table.add_row("Last Update:", f"{datetime.now().strftime('%H:%M:%S')}")
        return Panel(health_table, title="[bold]System Health[/bold]", border_style="green")

    def _generate_performance_panel(self):
        adapter_data, _ = self._get_api_data("/api/adapters/status")
        if not adapter_data:
            return Panel("[dim]Awaiting data...[/dim]", title="[bold]Performance[/bold]", border_style="yellow")

        total_races = sum(a.get('races_fetched', 0) for a in adapter_data)
        successful_adapters = sum(1 for a in adapter_data if a.get('status') == 'SUCCESS')
        success_rate = (successful_adapters / len(adapter_data) * 100) if adapter_data else 0

        perf_table = Table.grid(padding=(0, 1))
        perf_table.add_column(style="dim")
        perf_table.add_column(style="bold yellow")
        perf_table.add_row("Total Races:", str(total_races))
        perf_table.add_row("Success Rate:", f"{success_rate:.1f}%")
        return Panel(perf_table, title="[bold]Performance[/bold]", border_style="yellow")

    def _generate_adapter_panel(self):
        adapter_data, _ = self._get_api_data("/api/adapters/status")
        if not adapter_data:
            return Panel("[dim]Awaiting data...[/dim]", title="[bold]Adapter Status[/bold]", border_style="magenta")

        table = Table(title="Adapter Status", expand=True)
        table.add_column("Adapter", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Races", justify="right", style="magenta")
        table.add_column("Duration", justify="right", style="green")

        for adapter in sorted(adapter_data, key=lambda x: x.get('name', '')):
            status = Text("✅ SUCCESS", style="green") if adapter.get('status') == 'SUCCESS' else Text("❌ FAILED", style="red")
            table.add_row(
                adapter.get('name'),
                status,
                str(adapter.get('races_fetched', 0)),
                f"{adapter.get('fetch_duration', 0.0):.2f}s"
            )
        return Panel(table, title="[bold]Adapters[/bold]", border_style="magenta")

    def run(self):
        try:
            with Live(self.generate_layout(), screen=True, redirect_stderr=False) as live:
                while True:
                    time.sleep(REFRESH_INTERVAL)
                    live.update(self.generate_layout())
        except KeyboardInterrupt:
            self.console.print("👋 Monitoring stopped.")
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    # Load .env variables for standalone execution
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: dotenv is not installed. Script assumes environment variables are set.")

    display = LiveStatusDisplay()
    display.run()