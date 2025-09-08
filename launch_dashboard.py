import streamlit as st
import pandas as pd
import asyncio
from src.paddock_parser.pipeline import run_pipeline

st.set_page_config(layout="wide")

st.title("Paddock Parser NG - Enlightened Scorer Dashboard")

st.markdown("""
This dashboard allows you to run the Paddock Parser pipeline and view the results of the **Enlightened Scorer**.
The scorer analyzes races based on a "Trifecta of Factors": field size, favorite's odds, and contention.
Click the button below to fetch and analyze the latest race data.
""")

if 'race_data' not in st.session_state:
    st.session_state.race_data = None

if st.button("Run Analysis", type="primary"):
    with st.spinner("Running pipeline... This may take a moment."):
        # Streamlit runs in its own event loop, so we need to be careful.
        # The `asyncio.run` approach is simple for this proof-of-concept.
        try:
            races = asyncio.run(run_pipeline(min_runners=0, specific_source=None))

            if races:
                # Convert the list of NormalizedRace objects to a list of dictionaries
                race_list = []
                for race in races:
                    race_list.append({
                        "Track": race.track_name,
                        "Time": race.post_time.strftime("%H:%M") if race.post_time else "N/A",
                        "Race #": race.race_number,
                        "Runners": race.number_of_runners,
                        "Score": round(race.score, 2) if race.score is not None else 0.0,
                        "Fav Odds": round(race.scores.get('favorite_odds_score', 0), 2),
                        "Contention": round(race.scores.get('contention_score', 0), 2),
                        "Field Size": round(race.scores.get('field_size_score', 0), 3),
                    })

                # Create a pandas DataFrame
                df = pd.DataFrame(race_list)
                st.session_state.race_data = df
            else:
                st.session_state.race_data = pd.DataFrame() # Empty dataframe
                st.warning("No races were found by the pipeline.")

        except Exception as e:
            st.session_state.race_data = None
            st.error(f"An error occurred while running the pipeline: {e}")

if st.session_state.race_data is not None:
    if not st.session_state.race_data.empty:
        st.success("Analysis complete!")
        st.dataframe(st.session_state.race_data, use_container_width=True)
    else:
        # This handles the case where the button was clicked, but no data was returned.
        # We don't want to show a success message or an empty table without context.
        pass
