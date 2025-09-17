import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- Configuration ---
API_URL = "http://127.0.0.1:8000" # As per architectural mandate
st.set_page_config(layout="wide", page_title="Checkmate V3 Live Cockpit")

# --- Helper Functions ---
def get_mtp_style(mtp):
    """Returns a CSS color style based on minutes to post."""
    if mtp is None:
        return 'color: grey'
    if mtp <= 5:
        return 'color: red; font-weight: bold;'
    if mtp <= 15:
        return 'color: orange;'
    return 'color: green;'

def score_to_stars(score):
    """Converts a 0-100 score to a 5-star rating."""
    if score is None:
        return "N/A"
    return "★" * int(score / 20) if score is not None else ""

# --- Main Application ---
st.title("Checkmate V3 - Live Cockpit")

# Sidebar for controls and status
with st.sidebar:
    st.header("System Health")
    health_container = st.empty()
    st.header("Performance")
    perf_container = st.empty()

# Main content area for the live predictions table
st.header("Live Predictions")
placeholder = st.empty()

# --- Auto-refresh Loop ---
while True:
    try:
        # Update Health
        health_response = requests.get(f"{API_URL}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            health_container.json(health_data)
        else:
            health_container.error(f"Failed to fetch health data. Status: {health_response.status_code}")

        # Update Performance
        perf_response = requests.get(f"{API_URL}/performance")
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            perf_container.json(perf_data)
        else:
            perf_container.error(f"Failed to fetch performance data. Status: {perf_response.status_code}")

        # Update Live Predictions
        preds_response = requests.get(f"{API_URL}/predictions/active")
        if preds_response.status_code == 200:
            preds_data = preds_response.json()
            if preds_data:
                df = pd.DataFrame(preds_data)

                # Create display columns
                df['MTP'] = df['minutes_to_post'].round(1)
                df['Score'] = df['score_total'].apply(score_to_stars)

                # Select and reorder columns for display
                display_df = df[['race_key', 'MTP', 'Score', 'status', 'qualified_flag', 'stake_used']]

                # Apply styling
                styled_df = display_df.style.map(get_mtp_style, subset=['MTP'])

                placeholder.dataframe(styled_df)
            else:
                placeholder.info("No active predictions found.")
        else:
            placeholder.error(f"Failed to fetch active predictions. Status: {preds_response.status_code}")

    except requests.exceptions.ConnectionError:
        placeholder.error("Connection Error: Could not connect to the Checkmate API.")
        health_container.error("API Unreachable")
        perf_container.error("API Unreachable")
    except Exception as e:
        placeholder.error(f"An unexpected error occurred: {e}")

    # Add timestamp and sleep
    st.sidebar.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(30)
