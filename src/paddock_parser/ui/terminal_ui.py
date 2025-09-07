import inspect
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.logging import RichHandler

from .. import config
from ..base import NormalizedRace
from ..pipeline import run_pipeline
from ..scorer import get_high_roller_races, score_trifecta_factors
from ..models import Race as ScorerRace, Runner as ScorerRunner


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
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.progress = None
        self.progress_task = None
        self.log_handler = None

    def display_races(self, races: List[NormalizedRace]):
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
        if not races:
            info_message = (
                "[bold yellow]No races met the High Roller criteria.[/bold yellow]\n\n"
                "The report is filtered based on the following rules:\n"
                " - [bold]Time:[/bold] Only includes races starting in the next 25 minutes.\n"
                " - [bold]Runners:[/bold] Only includes races with Fewer than 7 runners."
            )
            self.console.print(info_message)
            return

        table = Table(title="[bold green]High Roller Report[/bold green]")
        table.add_column("Time", style="cyan")
        table.add_column("Venue", style="magenta")
        table.add_column("Favorite", style="green")
        table.add_column("Odds", style="yellow")

        for race in races:
            if not race.runners:
                continue

            favorite_runner = None
            min_odds = float('inf')
            for runner in race.runners:
                if runner.odds is not None and runner.odds < min_odds:
                    min_odds = runner.odds
                    favorite_runner = runner

            if favorite_runner:
                odds_str = f"{favorite_runner.odds:.2f}" if favorite_runner.odds is not None else "N/A"
                table.add_row(
                    race.race_time,
                    race.venue,
                    favorite_runner.name,
                    odds_str
                )

        self.console.print(table)

    def display_tiered_dashboard(self, tiered_data: dict):
        """Displays the tiered race data in a series of tables."""
        tier_titles = {
            "tier_1": "[bold green]== Tier 1: The Perfect Match ==[/bold green]",
            "tier_2": "[bold yellow]== Tier 2: The Strong Contenders ==[/bold yellow]",
            "tier_3": "[bold cyan]== Tier 3: The Singular Signals ==[/bold cyan]",
        }

        for tier_name, races in tiered_data.items():
            if races:
                table = Table(title=tier_titles[tier_name])
                table.add_column("Track", justify="left")
                table.add_column("Race #", justify="left")
                table.add_column("Post Time", justify="left")
                table.add_column("Runners", justify="left")

                for race in races:
                    post_time_str = race.race_time if race.race_time else "N/A"
                    num_runners = race.number_of_runners if race.number_of_runners is not None else len(race.runners)
                    table.add_row(
                        race.venue,
                        str(race.race_number),
                        post_time_str,
                        str(num_runners),
                    )
                self.console.print(table)

    def setup_logging(self):
        self.log_handler = RichHandler(console=self.console, show_path=False)

    def _display_main_menu(self):
        self.console.print("\n[bold magenta]Paddock Parser NG - Main Menu[/bold magenta]")
        self.console.print("1. Get Tiered Dashboard Report")
        self.console.print("2. Run Full Pipeline (Unfiltered)")
        self.console.print("3. View & Edit Settings")
        self.console.print("4. Quit")


    async def start_interactive_mode(self):
        while True:
            self._display_main_menu()
            choice = self.console.input("[bold]Select an option: [/bold]")
            if choice == '1':
                await self._run_tiered_dashboard_report()
            elif choice == '2':
                await self._run_full_pipeline_report()
            elif choice == '3':
                self._view_and_edit_settings()
            elif choice == '4':
                self.console.print("[yellow]Goodbye![/yellow]")
                break
            else:
                self.console.print("[bold red]Invalid option, please try again.[/bold red]")

    async def _run_tiered_dashboard_report(self):
        with self.console.status("Fetching data for Tiered Dashboard...", spinner="dots"):
            normalized_races, enabled_adapter_count, successful_adapter_count = await run_pipeline(
                min_runners=0,
                time_window_minutes=config.TIME_WINDOW_MINUTES,
                specific_source=None
            )

            if not normalized_races:
                self.console.print(
                    f"[yellow]No races found from {enabled_adapter_count} enabled adapters "
                    f"({successful_adapter_count} successfully returned data).[/yellow]"
                )
                return

            scorer_races = [
                race for race in
                (_convert_normalized_to_scorer_race(nr) for nr in normalized_races)
                if race is not None
            ]

            tiered_data = score_trifecta_factors(scorer_races)

        self.display_tiered_dashboard(tiered_data)


    async def _run_full_pipeline_report(self):
        with self.console.status("Running full unfiltered pipeline...", spinner="dots"):
            normalized_races, enabled_adapter_count, successful_adapter_count = await run_pipeline(
                min_runners=0,
                time_window_minutes=0, # No time filter
                specific_source=None
            )

            if not normalized_races:
                self.console.print(
                    f"[yellow]No races found from {enabled_adapter_count} enabled adapters "
                    f"({successful_adapter_count} successfully returned data).[/yellow]"
                )
                return

        self.display_races(normalized_races)

    def _view_and_edit_settings(self):
        """Displays current config settings and allows the user to edit them for the session."""
        while True:
            self.console.print("\n[bold cyan]Current Configuration Settings[/bold cyan]")

            settings = {name: getattr(config, name) for name in dir(config) if name.isupper()}

            table = Table(title="Configuration")
            table.add_column("Setting", style="magenta")
            table.add_column("Current Value", style="green")

            for name, value in settings.items():
                table.add_row(name, str(value))

            self.console.print(table)

            self.console.print("\nEnter the name of a setting to change, or type 'exit' to return to the main menu.")
            setting_to_change = self.console.input("[bold]Setting name: [/bold]").upper()

            if setting_to_change == 'EXIT':
                break

            if setting_to_change in settings:
                current_value = settings[setting_to_change]
                new_value_str = self.console.input(f"Enter new value for [magenta]{setting_to_change}[/magenta] (current: {current_value}): ")

                try:
                    # Attempt to cast to the same type as the original value
                    original_type = type(current_value)
                    if original_type == list:
                        # Simple list parsing for strings
                        new_value = [item.strip() for item in new_value_str.split(',')]
                    else:
                        new_value = original_type(new_value_str)

                    setattr(config, setting_to_change, new_value)
                    self.console.print(f"[green]'{setting_to_change}' updated to '{new_value}' for this session.[/green]")
                except (ValueError, TypeError) as e:
                    self.console.print(f"[bold red]Error: Invalid value. Could not convert '{new_value_str}' to the required type. {e}[/bold red]")
            else:
                self.console.print(f"[bold red]Error: Setting '{setting_to_change}' not found.[/bold red]")


    async def _run_high_roller_report(self):
        with self.console.status("Fetching data from providers...", spinner="dots"):
            normalized_races, enabled_adapter_count, successful_adapter_count = await run_pipeline(
                min_runners=0,
                time_window_minutes=0,  # High Roller does its own time filtering
                specific_source=None
            )

            if not normalized_races:
                self.console.print(
                    f"[yellow]No races found from {enabled_adapter_count} enabled adapters "
                    f"({successful_adapter_count} successfully returned data).[/yellow]"
                )
                return

            scorer_races = [
                race for race in
                (_convert_normalized_to_scorer_race(nr) for nr in normalized_races)
                if race is not None
            ]

            now = datetime.now()
            high_roller_races = get_high_roller_races(scorer_races, now)

        self.display_high_roller_report(high_roller_races)
