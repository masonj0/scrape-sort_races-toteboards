import pytest
import sys
from unittest.mock import patch, MagicMock, AsyncMock
import json

from src.checkmate_v7 import run
from src.checkmate_v7.models import Race, Runner, RaceDataSchema, HorseSchema, TrifectaFactorsSchema

@pytest.fixture
def mock_services():
    """Mocks the services used by the run.py script."""
    with patch('src.checkmate_v7.run.get_db_session') as mock_get_db, \
         patch('src.checkmate_v7.run.DataSourceOrchestrator') as mock_orchestrator, \
         patch('src.checkmate_v7.run.TrifectaAnalyzer') as mock_analyzer:

        # Configure Orchestrator Mock
        mock_orchestrator_instance = AsyncMock()
        mock_race = Race(
            race_id="R1",
            track_name="Test Track",
            race_number=1,
            post_time=None,
            runners=[Runner(name="Horse 1", odds=2.0, program_number=1)]
        )
        mock_orchestrator_instance.get_races.return_value = ([mock_race], [])
        mock_orchestrator.return_value = mock_orchestrator_instance

        # Configure Analyzer Mock
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.analyze_race.return_value = {
            "qualified": True,
            "checkmateScore": 85,
            "trifectaFactors": {} # Not needed for this test's assertions
        }
        mock_analyzer.return_value = mock_analyzer_instance

        yield mock_get_db, mock_orchestrator, mock_analyzer

@pytest.mark.anyio
async def test_run_script_json_output(capsys, mock_services):
    """
    Tests the run.py script with JSON output.
    """
    # Arrange
    test_args = ['run.py', '--output', 'json']
    _, mock_orchestrator, _ = mock_services
    mock_orchestrator.return_value.get_races.return_value = ([], [])

    with patch.object(sys, 'argv', test_args), \
         patch('builtins.open', new_callable=MagicMock) as mock_open:
        # Act
        await run.main()

    # Assert
    mock_open.assert_called_once()
