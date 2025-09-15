"""
Test for the consolidated Checkmate V7 script.
"""
import pytest
from unittest.mock import patch, MagicMock
import checkmate_v7

@pytest.mark.anyio
async def test_full_pipeline():
    """
    Tests the full pipeline in the consolidated script.
    We mock the database dependencies to verify persistence.
    """
    mock_session = MagicMock()
    mock_sessionmaker = MagicMock(return_value=mock_session)

    with patch('checkmate_v7.sessionmaker', mock_sessionmaker):
        with patch('checkmate_v7.create_engine'):
            await checkmate_v7.process_race_for_prediction_task()

    mock_sessionmaker.assert_called_once()
    mock_session.add.assert_called_once()
    added_obj = mock_session.add.call_args[0][0]
    assert isinstance(added_obj, checkmate_v7.Prediction)
    assert added_obj.favorite_candidate_name == "TestHorse"
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
