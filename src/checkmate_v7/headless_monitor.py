import requests
import time
import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

API_URL = "http://127.0.0.1:8000" # Base URL for the API
console = Console()

def get_mtp_style(minutes: float) -> str:
    """Returns the rich style string based on minutes to post."""
    if minutes < 5:
        return "bold red"
    elif 5 <= minutes <= 10:
        return "bold yellow"
    else:
        return "bold green"

def generate_layout() -> Panel:
    """Fetches all data from the API and builds a rich layout."""

    # In a real implementation, health and perf would be fetched.
    # For this focused recreation, we only need the predictions.
    try:
        preds_data = requests.get(f"{API_URL}/predictions/active").json()
    except requests.exceptions.RequestException as e:
        return Panel(f"Error: Cannot connect to the Checkmate API. Is it running?\n{e}", style="bold red")

    # Build Predictions Table
    preds_table = Table("Race Key", "Status", "MTP", "Score")
    # Sort by MTP to show most urgent races first
    for pred in sorted(preds_data, key=lambda p: p.get('minutes_to_post', 999)):
        mtp = pred.get('minutes_to_post', -1)
        score = pred.get('score_total') or 0

        style = get_mtp_style(mtp)
        mtp_display = f"[{style}]{mtp:.1f}[/]"

        preds_table.add_row(
            pred.get('race_key', 'N/A'),
            pred.get('status', 'N/A'),
            mtp_display,
            f"{score:.2f}"
        )

    # Combine into a master layout
    layout_str = f"[b]Checkmate V7 Live Cockpit[/b] - Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}\n\n{preds_table}"
    return Panel(layout_str)

if __name__ == "__main__":
    # A check to ensure the API is running would be good here.
    # For now, assume it is.
    with Live(generate_layout(), screen=True, redirect_stderr=False, refresh_per_second=0.1) as live:
        while True:
            time.sleep(30) # Refresh interval
            live.update(generate_layout())
