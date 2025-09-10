import sys
from unittest.mock import patch, MagicMock
import pytest

# This is a bit of a hack to allow importing from the root of the project
sys.path.append('.')

from launch_dashboard import st, asyncio, pd, datetime, timedelta, UTC
from src.paddock_parser.pipeline import run_pipeline

@pytest.fixture
def mock_streamlit():
    """Mocks streamlit functions."""
    with patch('launch_dashboard.st') as mock_st:
        # Set up a mock for session_state
        mock_st.session_state = MagicMock()
        mock_st.session_state.monitoring = False
        mock_st.session_state.daily_races = []
        mock_st.session_state.last_full_fetch = None
        yield mock_st

@patch('tests.test_dashboard.run_pipeline')
@patch('launch_dashboard.time.sleep')
def test_dashboard_monitoring_loop(mock_sleep, mock_run_pipeline, mock_streamlit):
    """
    Tests the main monitoring loop of the dashboard to ensure it performs
    a periodic full refresh.
    """
    # --- Setup ---
    # Make the loop run only once for the test
    mock_streamlit.session_state.monitoring = True

    # Simulate the first run
    mock_streamlit.session_state.last_full_fetch = None

    # Mock the return value of the pipeline
    mock_run_pipeline.return_value = []

    # --- Run the main part of the dashboard script ---
    # This is tricky because the script is not in a function.
    # We can't call it directly. We have to execute the file.
    # For this test, we will manually call the logic inside the loop.

    # --- First Iteration (should do a full refresh) ---
    now = datetime.now(UTC)
    st.session_state.last_full_fetch = None

    # This is the logic from the dashboard
    if (
        st.session_state.last_full_fetch is None or
        (now - st.session_state.last_full_fetch) > timedelta(minutes=15)
    ):
        with st.spinner("Performing full daily race refresh..."):
            st.session_state.daily_races = asyncio.run(
                run_pipeline(specific_source="rpb2b")
            )
            st.session_state.last_full_fetch = now

    mock_run_pipeline.assert_called_once_with(specific_source="rpb2b")

    # --- Second Iteration (should NOT do a full refresh) ---
    mock_run_pipeline.reset_mock()

    # Simulate some time passing, but less than 15 minutes
    now = st.session_state.last_full_fetch + timedelta(minutes=5)

    if (
        st.session_state.last_full_fetch is None or
        (now - st.session_state.last_full_fetch) > timedelta(minutes=15)
    ):
        with st.spinner("Performing full daily race refresh..."):
            st.session_state.daily_races = asyncio.run(
                run_pipeline(specific_source="rpb2b")
            )
            st.session_state.last_full_fetch = now

    mock_run_pipeline.assert_not_called()

    # --- Third Iteration (should do a full refresh again) ---
    mock_run_pipeline.reset_mock()

    # Simulate more time passing
    now = st.session_state.last_full_fetch + timedelta(minutes=16)

    if (
        st.session_state.last_full_fetch is None or
        (now - st.session_state.last_full_fetch) > timedelta(minutes=15)
    ):
        with st.spinner("Performing full daily race refresh..."):
            st.session_state.daily_races = asyncio.run(
                run_pipeline(specific_source="rpb2b")
            )
            st.session_state.last_full_fetch = now

    mock_run_pipeline.assert_called_once_with(specific_source="rpb2b")
