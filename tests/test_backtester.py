import pytest
from typing import List, Callable

# These updated models reflect the changes you will make in src/paddock_parser/models.py
from paddock_parser.models import Race, Runner

# The components you will be interacting with and creating
from paddock_parser.database.manager import DatabaseManager
from paddock_parser.backtester import Backtester

# --- Test Setup & Fixtures ---

@pytest.fixture
def historical_db_manager():
    """
    Sets up an in-memory SQLite database populated with historical race data,
    including designated winners for testing.
    """
    manager = DatabaseManager(db_path=":memory:")
    manager.create_tables() # Assumes this method exists from Operation Chronicle

    # Create historical races with clear winners
    races_to_save = [
        Race(race_id="R1", venue="VenueA", race_time="14:00", race_number=1, source="Test", is_handicap=False, runners=[
            Runner(name="Horse A (Fav)", odds="2/1", is_winner=False),
            Runner(name="Horse B (Winner)", odds="5/1", is_winner=True)
        ]),
        Race(race_id="R2", venue="VenueB", race_time="15:00", race_number=2, source="Test", is_handicap=False, runners=[
            Runner(name="Horse C (Winner, Fav)", odds="1/1", is_winner=True),
            Runner(name="Horse D", odds="8/1", is_winner=False)
        ]),
        Race(race_id="R3", venue="VenueC", race_time="16:00", race_number=3, source="Test", is_handicap=False, runners=[
            Runner(name="Horse E (Fav)", odds="3/1", is_winner=False),
            Runner(name="Horse F", odds="10/1", is_winner=False) # Race with no winner in data
        ]),
    ]

    for race in races_to_save:
        manager.save_race(race) # Assumes save_race is idempotent and handles winners

    yield manager
    manager.close()

def simple_favorite_picker(races: List[Race]) -> List[Race]:
    """ A simple scoring/selection algorithm for testing that picks the favorite. """
    # (A real algorithm would be more complex, but this is perfect for a test)
    for race in races:
        # Simplistic favorite identification
        race.runners.sort(key=lambda r: (r.odds == 'SP', float(r.odds.split('/')[0]) / float(r.odds.split('/')[1]) if '/' in r.odds else float('inf')))
    # Assume the strategy is to "bet" on the first runner (the favorite) of each race
    return races

# --- Test Cases for Operation Backtest ---

def test_backtester_initialization(historical_db_manager):
    """ SPEC: The Backtester should initialize correctly with a DatabaseManager instance. """
    backtester = Backtester(db_manager=historical_db_manager)
    assert backtester.db_manager is not None

def test_backtester_run_calculates_performance_correctly(historical_db_manager):
    """
    SPEC: The run method must execute a given strategy against all historical data,
    compare the top-ranked runner to the actual winner, and calculate the win rate.
    """
    # Arrange
    backtester = Backtester(db_manager=historical_db_manager)

    # Act
    # Run the backtest using our simple "pick the favorite" strategy
    results = backtester.run(strategy_func=simple_favorite_picker)

    # Assert
    # The backtester should have analyzed the 3 historical races.
    # The simple_favorite_picker strategy would have picked:
    # - R1: Horse A (Fav) -> Not a winner
    # - R2: Horse C (Winner, Fav) -> WINNER
    # - R3: Horse E (Fav) -> Not a winner

    assert "bets_placed" in results
    assert "winners_found" in results
    assert "win_rate" in results

    assert results["bets_placed"] == 3
    assert results["winners_found"] == 1
    assert results["win_rate"] == pytest.approx(1/3 * 100) # Check for approx. 33.33%

def test_backtester_handles_no_historical_data():
    """ SPEC: The backtester should not fail if the database is empty. """
    # Arrange
    empty_manager = DatabaseManager(db_path=":memory:")
    empty_manager.create_tables()
    backtester = Backtester(db_manager=empty_manager)

    # Act
    results = backtester.run(strategy_func=simple_favorite_picker)

    # Assert
    assert results["bets_placed"] == 0
    assert results["winners_found"] == 0
    assert results["win_rate"] == 0.0
