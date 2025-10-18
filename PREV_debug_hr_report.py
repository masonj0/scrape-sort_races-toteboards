import asyncio
from src.paddock_parser.ui.terminal_ui import TerminalUI

def run_report():
    ui = TerminalUI()
    asyncio.run(ui._run_high_roller_report())

if __name__ == "__main__":
    run_report()
