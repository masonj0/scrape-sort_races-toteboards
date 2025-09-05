from datetime import datetime
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.logging import RichHandler

from ..base import NormalizedRace
from ..pipeline import run_pipeline
from ..scorer import get_high_roller_races
from ..models import Race as ScorerRace, Runner as ScorerRunner

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

    def display_high_roller_report(self, races: List[ScorerRace]):
        """
        Displays the high roller report in a rich, formatted table.
        """
        if not races:
            info_message = (
                "[bold yellow]No races met the High Roller criteria.[/bold yellow]\n\n"
                "The report is filtered based on the following rules:\n"
                " - [bold]Time:[/bold] Only includes races starting in the next 25 minutes.\n"
                " - [bold]Runners:[/bold] Only includes races with Fewer than 7 runners."
            )
            self.console.print(info_message)
            return

        table = Table(title="High Roller Report")

        table.add_column("Time", style="cyan")
        table.add_column("Venue", style="magenta")
        table.add_column("Favorite", style="green")
        table.add_column("Odds", style="yellow")

        for race in races:
            # The high roller report logic implies one favorite runner per race.
            if race.runners:
                favorite = race.runners[0]
                odds_str = f"{favorite.odds:.2f}" if favorite.odds is not None else "N/A"
                table.add_row(
                    race.race_time,
                    race.venue,
                    favorite.name,
                    odds_str
                )

        self.console.print(table)

    def start_fetching_progress(self, num_tasks: int):
        """Initializes and starts a progress bar for fetching races."""
        self.progress = Progress(console=self.console)
        self.progress.start()
        self.progress_task = self.progress.add_task("Fetching races...", total=num_tasks)

    def update_fetching_progress(self):
        """Advances the fetching progress bar by one step."""
        if self.progress and self.progress_task is not None:
            self.progress.update(self.progress_task, advance=1)

    def stop_fetching_progress(self):
        """Stops the progress bar and cleans up."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.progress_task = None

    def setup_logging(self):
        """Creates a RichHandler and sets it up."""
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
        high_roller_races = None
        with self.console.status("Fetching data from providers...", spinner="dots"):
            normalized_races = await run_pipeline(min_runners=0, specific_source=None) # No longer pass UI

            if not normalized_races:
                self.console.print("[yellow]No races were found by the pipeline.[/yellow]")
                return

            # Adapt from NormalizedRace to the ScorerRace model
            scorer_races = []
            for norm_race in normalized_races:
                if norm_race.post_time:
                    scorer_runners = [ScorerRunner(name=r.name, odds=r.odds) for r in norm_race.runners]
                    scorer_races.append(
                        ScorerRace(
                            race_id=norm_race.race_id,
                            venue=norm_race.track_name,
                            race_number=norm_race.race_number,
                            race_time=norm_race.post_time.strftime("%H:%M"),
                            is_handicap=norm_race.race_type == "Handicap",
                            runners=scorer_runners
                        )
                    )

            now = datetime.now()
            high_roller_races = get_high_roller_races(scorer_races, now)

        self.display_high_roller_report(high_roller_races)
