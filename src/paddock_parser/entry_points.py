import asyncio
import subprocess
import sys
from pathlib import Path

def run_terminal_ui():
    """Entry point for the terminal user interface."""
    # This is a bit of a hack to make sure the UI can be imported
    # when run as a script. We add the parent directory of the package
    # to the path.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from paddock_parser.ui.terminal_ui import TerminalUI

    ui = TerminalUI()
    asyncio.run(ui.start_interactive_mode())

def run_dashboard():
    """Entry point for the Streamlit dashboard."""
    dashboard_path = Path(__file__).resolve().parents[2] / "launch_dashboard.py"
    subprocess.run(["streamlit", "run", str(dashboard_path)])

if __name__ == '__main__':
    # This allows running the entry points directly for testing
    # e.g., python -m src.paddock_parser.entry_points ui
    if len(sys.argv) > 1 and sys.argv[1] == 'ui':
        run_terminal_ui()
    elif len(sys.argv) > 1 and sys.argv[1] == 'dashboard':
        run_dashboard()
    else:
        print("Usage: python -m src.paddock_parser.entry_points [ui|dashboard]")
