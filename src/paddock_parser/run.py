"""
This file is intentionally left as a library and not an entry point.
The main entry point for the application is `launch_paddock_parser.py`.
"""

import argparse
import logging
import asyncio

from .pipeline import run_pipeline
from .ui.terminal_ui import TerminalUI
from . import version
from . import config
