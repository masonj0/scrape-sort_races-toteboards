from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.logging import RichHandler

from ..base import NormalizedRace

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
        self.log_handler = RichHandler(console=self.console, show_path=False, show_level=False, show_time=False)
