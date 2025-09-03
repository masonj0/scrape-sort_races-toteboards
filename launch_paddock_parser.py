#!/usr/bin/env python3

import asyncio
from src.paddock_parser.ui.terminal_ui import TerminalUI

def launch():
    """
    Initializes and runs the Paddock Parser Terminal UI.
    """
    ui = TerminalUI()
    asyncio.run(ui.start_interactive_mode())

if __name__ == "__main__":
    launch()
