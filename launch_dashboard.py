import time
import asyncio
import pandas as pd
import streamlit as st
from datetime import datetime, UTC, timedelta

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
if 'daily_races' not in st.session_state:
    st.session_state.daily_races = []
if 'last_full_fetch' not in st.session_state:
    st.session_state.last_full_fetch = None

# --- Control Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Monitoring", type="primary"):
        st.session_state.monitoring = True
        st.session_state.last_full_fetch = None # Reset on start
        st.experimental_rerun()

with col2:
    if st.button("Stop Monitoring"):
        st.session_state.monitoring = False
        st.experimental_rerun()

# --- Live Monitoring Loop ---
if st.session_state.monitoring:
    st.success("Monitoring for Checkmate opportunities... The dashboard will update automatically.")

    placeholder = st.empty()

    while st.session_state.monitoring:
        now = datetime.now(UTC)

        # Perform a full refresh every 15 minutes
        if (
            st.session_state.last_full_fetch is None or
            (now - st.session_state.last_full_fetch) > timedelta(minutes=15)
        ):
            with st.spinner("Performing full daily race refresh..."):
                st.session_state.daily_races = asyncio.run(
                    run_pipeline(specific_source="rpb2b")
                )
                st.session_state.last_full_fetch = now

        with placeholder.container():
            st.write(f"Last check: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

            imminent_races = [
                race for race in st.session_state.daily_races
                if race.post_time and (now - timedelta(minutes=2)) < race.post_time <= (now + timedelta(minutes=10))
            ]

            if not imminent_races:
                st.info("No races are imminent. Waiting for the next check...")
            else:
                imminent_race_ids = [race.race_id for race in imminent_races]
                st.info(f"Found {len(imminent_races)} imminent races. Fetching live odds...")

                with st.spinner(f"Fetching details for {len(imminent_races)} races..."):
                    try:
                        live_races = asyncio.run(
                            run_pipeline(specific_source="rpb2b", race_ids=imminent_race_ids)
                        )

                        checkmate_races = find_checkmate_opportunities(live_races)

                        if checkmate_races:
                            st.header("🚨 Checkmate Opportunity Found! 🚨")
                            st.balloons()

                            race_list = []
                            for race in checkmate_races:
                                race_list.append({
                                    "Track": race.track_name,
                                    "Time": race.post_time.strftime("%H:%M") if race.post_time else "N/A",
                                    "MTP": int((race.post_time - now).total_seconds() / 60) if race.post_time else "N/A",
                                    "Race #": race.race_number,
                                    "Runners": race.number_of_runners,
                                    "Fav Odds": next((r.odds for r in sorted(race.runners, key=lambda r: r.odds or float('inf'))), 0),
                                    "2nd Fav Odds": next((r.odds for r in sorted(race.runners, key=lambda r: r.odds or float('inf'))[1:]), 0)
                                })
                            df = pd.DataFrame(race_list)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No Checkmate opportunities in the imminent races.")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

        time.sleep(60)
        st.experimental_rerun()
else:
    st.info("Monitoring is stopped. Click 'Start Monitoring' to begin.")
