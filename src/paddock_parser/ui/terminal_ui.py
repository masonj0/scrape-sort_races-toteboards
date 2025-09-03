import logging
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import asyncio
from datetime import datetime
from rich.logging import RichHandler
from rich.panel import Panel

from ..base import NormalizedRace
from ..pipeline import run_pipeline
from ..scorer import get_high_roller_races_for_normalized_data

class TerminalUI:
    """
    A class to handle all terminal output using the rich library.
    """
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.progress = None
        self.progress_task = None
        self.log_handler = None

    def display_races(self, races: List[NormalizedRace]):
        """
        Displays a list of races in a formatted table.
        """
        table = Table(title="Race Information")

        table.add_column("Track", justify="left")
        table.add_column("Race #", justify="left")
        table.add_column("Post Time", justify="left")
        table.add_column("Runners", justify="left")
        table.add_column("Score", justify="left")

        for race in races:
            post_time_str = race.post_time.strftime("%H:%M") if race.post_time else "N/A"
            score_str = f"{race.score:.0f}" if race.score is not None else "N/A"

            table.add_row(
                race.track_name,
                str(race.race_number),
                post_time_str,
                str(race.number_of_runners),
                score_str
            )

        self.console.print(table)

    def start_fetching_progress(self, num_tasks: int):
        """
        Initializes and starts a progress bar for fetching races.
        """
        self.progress = Progress(console=self.console)
        self.progress.start()
        self.progress_task = self.progress.add_task("Fetching races...", total=num_tasks)

    def update_fetching_progress(self):
        """
        Advances the fetching progress bar by one step.
        """
        if self.progress and self.progress_task is not None:
            self.progress.update(self.progress_task, advance=1)

    def stop_fetching_progress(self):
        """
        Stops the progress bar and cleans up.
        """
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.progress_task = None

    def setup_logging(self):
        """
        Creates a RichHandler and sets it up.
        The calling code is responsible for adding it to a logger.
        """
        self.log_handler = RichHandler(console=self.console, show_path=False)

    def _display_main_menu(self):
        """Displays the main menu options."""
        self.console.print("\n[bold magenta]Paddock Parser NG - Main Menu[/bold magenta]")
        self.console.print("1. Get High Roller Report")
        self.console.print("2. Quit")

    async def start_interactive_mode(self):
        """Starts the main interactive loop for the UI."""
        while True:
            self._display_main_menu()
            choice = self.console.input("[bold]Select an option: [/bold]")

            if choice == '1':
                await self._run_high_roller_report()
            elif choice == '2':
                self.console.print("[yellow]Goodbye![/yellow]")
                break
            else:
                self.console.print("[bold red]Invalid option, please try again.[/bold red]")

    async def _run_high_roller_report(self):
        """Runs the full pipeline and displays the high roller report."""
        self.console.print(Panel("[bold green]Generating High Roller Report...[/bold green]", expand=False))

        # For this specific report, we want to bypass the pipeline's min_runners filter
        # as the high roller logic has its own runner count criteria.
        all_races = await run_pipeline(min_runners=0, specific_source=None)

        if not all_races:
            self.console.print("[yellow]No races were found by the pipeline.[/yellow]")
            return

        now = datetime.now()
        high_roller_races = get_high_roller_races_for_normalized_data(all_races, now)

        if not high_roller_races:
            self.console.print(Panel("[bold yellow]No races met the High Roller criteria.[/bold yellow]", expand=False))
        else:
            self.console.print(Panel("[bold blue]High Roller Report[/bold blue]", expand=False))
            # The display_races function needs a 'score' attribute, which our new function provides.
            # It also needs a 'track_name', 'race_number', 'post_time', and 'number_of_runners',
            # all of which are present in NormalizedRace.
            self.display_races(high_roller_races)
