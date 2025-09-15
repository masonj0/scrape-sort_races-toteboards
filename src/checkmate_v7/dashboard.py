import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Checkmate V7 Live Cockpit",
    layout="wide",
)

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000"
PREDICTIONS_ENDPOINT = f"{API_URL}/predictions/active"

# --- Helper Functions ---

@st.cache_data(ttl=30)
def get_predictions():
    """Fetches active predictions from the API and returns a DataFrame."""
    try:
        response = requests.get(PREDICTIONS_ENDPOINT)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except (requests.exceptions.RequestException, ValueError):
        # Return empty dataframe on error, will be handled in the main loop
        return pd.DataFrame()

def score_to_stars(score: float) -> str:
    """Converts a numerical score (0-100) to a 5-star rating."""
    if pd.isna(score):
        return "N/A"
    filled_stars = int(score / 20)
    return "★" * filled_stars + "☆" * (5 - filled_stars)

def style_mtp(val: float) -> str:
    """Applies background color styling to the MTP column."""
    if val < 5:
        color = '#ffadad'  # Light Red
    elif 5 <= val <= 10:
        color = '#ffd6a5'  # Light Orange/Yellow
    else:
        color = '#caffbf'  # Light Green
    return f'background-color: {color}'

# --- Main Page Layout ---

st.title("Checkmate V7 Live Cockpit")

placeholder = st.empty()

while True:
    with placeholder.container():
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        df = get_predictions()

        if not df.empty:
            # --- Data Transformation ---
            df_display = df[['race_key', 'minutes_to_post', 'score_total']].copy()
            df_display.rename(columns={
                'race_key': 'Race',
                'minutes_to_post': 'MTP',
                'score_total': 'Score'
            }, inplace=True)

            # Sort by MTP
            df_display.sort_values(by='MTP', inplace=True)

            # Create visual score column
            df_display['Rating'] = df_display['Score'].apply(score_to_stars)

            # --- Display Table with Formatting ---
            st.dataframe(
                df_display[['Race', 'MTP', 'Rating', 'Score']].style
                .map(style_mtp, subset=['MTP'])
                .format({'MTP': '{:.1f}', 'Score': '{:.2f}'}),
                use_container_width=True
            )
        else:
            st.warning("No active predictions found or API is unavailable.")

    time.sleep(30)
