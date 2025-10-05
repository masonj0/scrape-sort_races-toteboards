import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Checkmate Command Deck")
load_dotenv() # Load .env file

API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("DEV_API_KEY", "test_api_key") # Default to test_api_key if not in .env
HEADERS = {"X-API-Key": API_KEY}

# --- Helper Functions ---
@st.cache_data(ttl=60) # Cache data for 60 seconds
def get_api_data(endpoint: str):
    """Fetches data from a given API endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS)
        response.raise_for_status() # Raises an exception for 4XX/5XX errors
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# --- UI Layout ---
st.title("🚀 Checkmate Command Deck")
st.markdown("Real-time operational dashboard for the Ultimate Solo backend.")

# --- Data Display ---
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Qualified Races")
    if st.button("Refresh Qualified Races"):
        st.cache_data.clear()

    qualified_data, error = get_api_data("/api/races/qualified")
    if error:
        st.error(f"**Failed to fetch qualified races:**\\n\\n{error}")
    elif qualified_data:
        if qualified_data:
            df = pd.json_normalize(qualified_data, record_path=['runners'], meta=['race_id', 'venue', 'race_number', 'start_time'])
            st.dataframe(df)
        else:
            st.info("No qualified races found at this time.")
    else:
        st.info("Awaiting data...")

with col2:
    st.header("📊 Adapter Status")
    if st.button("Refresh Adapter Status"):
        st.cache_data.clear()

    status_data, error = get_api_data("/api/adapters/status")
    if error:
        st.error(f"**Failed to fetch adapter status:**\\n\\n{error}")
    elif status_data:
        st.dataframe(pd.DataFrame(status_data))
    else:
        st.info("Awaiting data...")

# --- Instructions ---
st.sidebar.header("How to Use")
st.sidebar.info(
    "This dashboard polls the local FastAPI backend.\\n\\n"
    "1. Ensure the backend is running (`run_backend.bat`).\\n"
    "2. Use the 'Refresh' buttons to get the latest data.\\n"
    "3. The data is cached for 60 seconds to avoid spamming the API."
)