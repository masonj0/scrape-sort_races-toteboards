import time
import asyncio
import pandas as pd
import streamlit as st
from datetime import datetime, UTC

from src.paddock_parser.pipeline import run_pipeline
from src.paddock_parser.scorer import find_checkmate_opportunities

st.set_page_config(layout="wide")

st.title("Paddock Parser NG - Checkmate Alert System")

st.markdown(
    """
    This dashboard continuously monitors for the "Checkmate" betting opportunity.
    When a race meets the specified criteria and is near its post time, an alert
    will be displayed.
    """
)

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'last_run' not in st.session_state:
    st.session_state.last_run = None

# --- Control Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Monitoring", type="primary"):
        st.session_state.monitoring = True
        st.session_state.last_run = datetime.now(UTC)

with col2:
    if st.button("Stop Monitoring"):
        st.session_state.monitoring = False

# --- Live Monitoring Loop ---
if st.session_state.monitoring:
    st.success("Monitoring for Checkmate opportunities... The dashboard will update automatically.")

    # Create placeholders for live data
    placeholder = st.empty()

    while st.session_state.monitoring:
        with placeholder.container():
            st.write(f"Last check: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC")

            with st.spinner("Running pipeline for `rpb2b` adapter..."):
                try:
                    races = asyncio.run(
                        run_pipeline(min_runners=0, time_window_minutes=120, specific_source="rpb2b")
                    )

                    if races:
                        checkmate_races = find_checkmate_opportunities(races)

                        alert_races = []
                        for race in checkmate_races:
                            if race.post_time:
                                time_diff = race.post_time - datetime.now(UTC)
                                minutes_to_post = time_diff.total_seconds() / 60
                                if 0 <= minutes_to_post <= 5:
                                    alert_races.append(race)

                        if alert_races:
                            st.header("🚨 Checkmate Opportunity Found! 🚨")
                            st.balloons()

                            race_list = []
                            for race in alert_races:
                                race_list.append({
                                    "Track": race.track_name,
                                    "Time": race.post_time.strftime("%H:%M") if race.post_time else "N/A",
                                    "Race #": race.race_number,
                                    "Runners": race.number_of_runners,
                                    "Fav Odds": next((r.odds for r in sorted(race.runners, key=lambda r: r.odds or float('inf'))), 0),
                                    "2nd Fav Odds": next((r.odds for r in sorted(race.runners, key=lambda r: r.odds or float('inf'))[1:]), 0)
                                })
                            df = pd.DataFrame(race_list)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No imminent Checkmate opportunities found. Continuing to monitor...")
                    else:
                        st.warning("No races were found by the pipeline in the last run.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

        # Wait for 60 seconds before the next run
        time.sleep(60)

        # Rerun the script to update the dashboard
        st.experimental_rerun()
else:
    st.info("Monitoring is stopped. Click 'Start Monitoring' to begin.")
