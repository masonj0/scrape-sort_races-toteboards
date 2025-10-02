import pytest
from unittest.mock import patch
from src.paddock_parser.adapters.fanduel_graphql_adapter import FanDuelGraphQLAdapter
from src.paddock_parser.base import NormalizedRace, NormalizedRunner

@pytest.fixture
def mock_graphql_response():
    """Provides a mock of the raw GraphQL API response."""
    return {
        "data": {
            "allRaces": {
                "edges": [
                    {
                        "node": {
                            "trackName": "Saratoga",
                            "raceNumber": 1,
                            "postTime": "2025-09-08T18:00:00.000Z",
                            "runners": [
                                {"runnerName": "Horse A", "odds": "5/2", "scratched": False},
                                {"runnerName": "Horse B", "odds": "3/1", "scratched": True},
                                {"runnerName": "Horse C", "odds": "10/1", "scratched": False},
                            ]
                        }
                    },
                    {
                        "node": {
                            "trackName": "Del Mar",
                            "raceNumber": 5,
                            "postTime": "2025-09-08T20:30:00.000Z",
                            "runners": [
                                {"runnerName": "Horse D", "odds": "1/1", "scratched": False}
                            ]
                        }
                    }
                ]
            }
        }
    }

def test_parse_races(mock_graphql_response):
    """
    SPEC: `parse_races` should correctly parse the GraphQL JSON into NormalizedRace objects.
    """
    adapter = FanDuelGraphQLAdapter()
    races = adapter.parse_races(mock_graphql_response)

    assert len(races) == 2

    # Test Race 1 (Saratoga)
    saratoga_race = races[0]
    assert saratoga_race.track_name == "Saratoga"
    assert saratoga_race.race_number == 1
    assert saratoga_race.number_of_runners == 2 # Horse B is scratched
    assert len(saratoga_race.runners) == 2

    # Test Runner A
    runner_a = saratoga_race.runners[0]
    assert runner_a.name == "Horse A"
    assert runner_a.odds == pytest.approx(3.5) # 5/2 + 1

    # Test Race 2 (Del Mar)
    delmar_race = races[1]
    assert delmar_race.track_name == "Del Mar"
    assert delmar_race.race_number == 5
    assert delmar_race.runners[0].odds == pytest.approx(2.0) # 1/1 + 1

@patch('src.paddock_parser.adapters.fanduel_graphql_adapter.post_page_content')
def test_fetch_uses_sync_fetcher(mock_post_page_content, mock_graphql_response):
    """
    SPEC: The `fetch` method must use the `post_page_content` sync_fetcher.
    """
    mock_post_page_content.return_value = mock_graphql_response
    adapter = FanDuelGraphQLAdapter()

    # Since fetch is async but calls sync code, we need to run it in an event loop
    import asyncio
    races = asyncio.run(adapter.fetch())

    mock_post_page_content.assert_called_once()
    assert len(races) == 2
    assert races[0].track_name == "Saratoga"
