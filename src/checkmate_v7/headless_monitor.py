import requests
import time
import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import pandas as pd

API_URL = "http://127.0.0.1:8000" # Corrected API URL
console = Console()

def get_mtp_style_rich(mtp):
    """Returns a rich style string based on minutes to post."""
    if mtp is None:
        return "grey"
    if mtp <= 5:
        return "bold red"
    if mtp <= 15:
        return "orange3"
    return "green"

def score_to_stars(score):
    """Converts a 0-100 score to a 5-star rating."""
    if score is None:
        return "N/A"
    return "★" * int(score / 20) if score is not None else ""

def generate_layout() -> Panel:
    """Fetches all data from the API and builds a rich layout."""
    try:
        health_data = requests.get(f"{API_URL}/health").json()
        perf_data = requests.get(f"{API_URL}/performance").json()
        preds_data = requests.get(f"{API_URL}/predictions/active").json()
    except requests.exceptions.ConnectionError:
        return Panel("Error: Cannot connect to the Checkmate API. Is it running?", style="bold red")
    except requests.exceptions.JSONDecodeError:
        return Panel("Error: Failed to decode JSON from API.", style="bold red")

    # Build Health Panel
    health_panel = Panel(f"DB: {health_data.get('database', 'N/A')} | Worker: {health_data.get('celery', 'N/A')}", title="System Health")

    # Build Performance Panel
    metrics = perf_data
    roi = metrics.get('roi_percent', 0)
    n = metrics.get('sample_size', 0)
    display_string = f"ROI: {roi:.2f}% (n={n})"
    perf_panel = Panel(display_string, title="Performance")

    # Build Predictions Table
    preds_table = Table("Race Key", "MTP", "Score", "Status", "Qualified", "Stake")
    if preds_data:
        df = pd.DataFrame(preds_data)
        for _, pred in df.iterrows():
            mtp = pred.get('minutes_to_post')
            mtp_display = f"[{get_mtp_style_rich(mtp)}]{mtp:.1f}[/]" if mtp is not None else "N/A"

            score = pred.get('score_total')
            score_display = score_to_stars(score)

            stake = pred.get('stake_used', 0)
            stake_display = f"${stake:.2f}" if stake is not None else "N/A"

            preds_table.add_row(
                pred['race_key'],
                mtp_display,
                score_display,
                pred['status'],
                str(pred.get('qualified_flag', 'N/A')),
                stake_display
            )

    # Combine into a master layout
    main_panel_content = f"{health_panel}\n{perf_panel}\n{preds_table}"
    layout = Panel(
        main_panel_content,
        title=f"[b]Checkmate V3 Headless Monitor[/b] - Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}",
        border_style="blue"
    )
    return layout

if __name__ == "__main__":
    with Live(generate_layout(), screen=True, redirect_stderr=False, refresh_per_second=0.1) as live:
        try:
            while True:
                time.sleep(10)
                live.update(generate_layout())
        except KeyboardInterrupt:
            console.print("Monitor stopped.")
