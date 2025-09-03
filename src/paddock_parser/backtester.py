from typing import List, Callable, Dict, Any
from .database.manager import DatabaseManager
from .models import Race

class Backtester:
    """
    A class to backtest scoring strategies against historical race data.
    """
    def __init__(self, db_manager: DatabaseManager):
        """Initializes the Backtester with a DatabaseManager instance."""
        self.db_manager = db_manager

    def run(self, strategy_func: Callable[[List[Race]], List[Race]]) -> Dict[str, Any]:
        """
        Runs a given strategy function against historical data and calculates performance.
        """
        # 1. Fetch all historical races from the database
        historical_races = self.db_manager.get_all_races()

        # 2. Handle the case where there is no historical data
        if not historical_races:
            return {
                "bets_placed": 0,
                "winners_found": 0,
                "win_rate": 0.0,
            }

        # 3. Apply the selection strategy to the historical data
        # The strategy function should return the races with the "picked" runner
        # at index 0 of the runners list.
        races_with_picks = strategy_func(historical_races)

        # 4. Analyze the results
        bets_placed = 0
        winners_found = 0

        for race in races_with_picks:
            bets_placed += 1

            # Check if the strategy made a pick (i.e., there's at least one runner)
            if race.runners:
                picked_runner = race.runners[0]

                # Check if the picked runner was the actual winner
                if picked_runner.is_winner:
                    winners_found += 1

        # 5. Calculate the final win rate
        win_rate = (winners_found / bets_placed) * 100 if bets_placed > 0 else 0.0

        # 6. Return the performance results
        return {
            "bets_placed": bets_placed,
            "winners_found": winners_found,
            "win_rate": win_rate,
        }
