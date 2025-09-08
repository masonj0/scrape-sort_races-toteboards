from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.logging import RichHandler

from ..base import NormalizedRace
from ..pipeline import run_pipeline
from ..scorer import score_races
from ..models import Race as ScorerRace, Runner as ScorerRunner
from ..config import LOG_FILE_PATH
from ..log_analyzer import analyze_log_file


def _convert_normalized_to_scorer_race(norm_race: NormalizedRace) -> Optional[ScorerRace]:
    """Converts a NormalizedRace to the ScorerRace model for use with scorer functions."""
    if not norm_race.post_time:
        return None

    scorer_runners = [ScorerRunner(name=r.name, odds=r.odds) for r in norm_race.runners]
    is_handicap = norm_race.race_type and "handicap" in norm_race.race_type.lower()

    return ScorerRace(
        race_id=norm_race.race_id,
        venue=norm_race.track_name,
        race_number=norm_race.race_number,
        race_time=norm_race.post_time.strftime("%H:%M"),
        number_of_runners=norm_race.number_of_runners,
        is_handicap=is_handicap,
        runners=scorer_runners,
    )


class TerminalUI:
    """
    A class to handle all terminal output using the rich library.
    """
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.progress = None
        self.progress_task = None
        self.log_handler = None

    def display_scoring_report(self, races: List[NormalizedRace]):
        """
        Displays the dynamic scoring report in a rich, formatted table.
        NOTE: This expects races to already be sorted by the pipeline.
        """
        if not races:
            self.console.print("[bold yellow]No races were found to score.[/bold yellow]")
            return

        table = Table(title="[bold green]Dynamic Scoring Report[/bold green]")
        table.add_column("Race Time", style="cyan")
        table.add_column("Venue", style="magenta")
        table.add_column("Race #", style="white")
        table.add_column("Runners", style="white")
        table.add_column("Handicap", style="white")
        table.add_column("Fav Odds", style="yellow")
        table.add_column("Contention", style="yellow")
        table.add_column("Field Size", style="yellow")
        table.add_column("Total Score", style="bold green")

        for race in races:
            scores = getattr(race, 'scores', {})
            post_time_str = race.post_time.strftime("%H:%M") if race.post_time else "N/A"
            is_handicap_str = "Yes" if (race.race_type and "handicap" in race.race_type.lower()) else "No"

            table.add_row(
                post_time_str,
                race.track_name,
                str(race.race_number),
                str(race.number_of_runners),
                is_handicap_str,
                f"{scores.get('favorite_odds_score', 0):.2f}",
                f"{scores.get('contention_score', 0):.2f}",
                f"{scores.get('field_size_score', 0):.3f}",
                f"{scores.get('total_score', 0):.2f}",
            )
        self.console.print(table)

    def display_log_analysis_report(self):
        """
        Analyzes the log file and displays a summary report.
        """
        self.console.print(f"\n[bold]Analyzing log file at:[/] [cyan]{LOG_FILE_PATH}[/cyan]")
        log_counts = analyze_log_file(LOG_FILE_PATH)

        if not log_counts:
            self.console.print("[yellow]No log data found or file could not be read.[/yellow]")
            return

        table = Table(title="[bold blue]Log File Analysis[/bold blue]")
        table.add_column("Log Level", style="cyan")
        table.add_column("Count", style="magenta", justify="right")

        for level, count in sorted(log_counts.items()):
            table.add_row(level, str(count))
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
        self.console.print("1. Get Dynamic Scoring Report")
        self.console.print("2. View Log Analysis Report")
        self.console.print("3. Quit")

    async def start_interactive_mode(self):
        """Starts the main interactive loop for the UI."""
        while True:
            self._display_main_menu()
            choice = self.console.input("[bold]Select an option: [/bold]")
            if choice == '1':
                await self._run_scoring_report()
            elif choice == '2':
                self.display_log_analysis_report()
            elif choice == '3':
                self.console.print("[yellow]Goodbye![/yellow]")
                break
            else:
                self.console.print("[bold red]Invalid option, please try again.[/bold red]")

    async def _run_scoring_report(self):
        """Runs the full pipeline and displays the dynamic scoring report."""
        with self.console.status("Fetching data from providers...", spinner="dots"):
            scored_races = await run_pipeline(min_runners=0, specific_source=None)

        if not scored_races:
            self.console.print("[yellow]No races were found by the pipeline.[/yellow]")
            return
        self.display_scoring_report(scored_races)
