import requests
import time
import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

API_URL = "http://127.0.0.1:8000/api/v1"
console = Console()

def generate_layout() -> Panel:
    """Fetches all data from the API and builds a rich layout."""

    # Fetch data from all relevant endpoints
    try:
        health_data = requests.get(f"{API_URL}/health").json()
        perf_data = requests.get(f"{API_URL}/performance").json()
        preds_data = requests.get(f"{API_URL}/predictions/active").json()
    except requests.ConnectionError:
        return Panel("Error: Cannot connect to the Checkmate API. Is it running?", style="bold red")

    # Build Health Panel
    health_panel = Panel(f"DB: {health_data['database_status']} | Worker: {health_data['celery_status']}", title="System Health")

    # Build Performance Panel
    metrics = perf_data
    ci = metrics.get('roi_confidence_interval')
    if ci and ci is not None:
         display_string = f"ROI: {metrics['roi_percentage']:.2f}% (95% CI: [{ci[0]:.2f}%, {ci[1]:.2f}%], n={metrics['sample_size_n']})"
    else:
        display_string = f"ROI: {metrics['roi_percentage']:.2f}% (n={metrics['sample_size_n']})"
    perf_panel = Panel(display_string, title="Performance")

    # Build Predictions Table
    preds_table = Table("Race Key", "Status", "Stake")
    for pred in preds_data:
        preds_table.add_row(pred['race_key'], pred['status'], f"${pred['stake_used']:.2f}")

    # Combine into a master layout
    layout = f"[b]Checkmate V3 Headless Monitor[/b] - Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}\\n{health_panel}\\n{perf_panel}\\n{preds_table}"
    return Panel(layout)

if __name__ == "__main__":
    with Live(generate_layout(), screen=True, redirect_stderr=False) as live:
        while True:
            time.sleep(10) # Refresh interval
            live.update(generate_layout())
