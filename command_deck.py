import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Checkmate Command Deck")
load_dotenv() # Load .env file

API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("DEV_API_KEY", "test_api_key")
HEADERS = {"X-API-Key": API_KEY}

# --- Helper Functions ---
@st.cache_data(ttl=30)
def get_api_data(endpoint: str):
    """Fetches data from a given API endpoint."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        st.write(f"*Fetching data from: `{url}`*")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# --- UI Layout ---
st.title("🚀 Checkmate Command Deck")
st.markdown("Real-time operational dashboard for the Ultimate Solo backend.")

# --- Sidebar Controls ---
st.sidebar.header("Controls")
analyzer_selection = st.sidebar.selectbox(
    'Select Analyzer',
    ['trifecta'] # In the future, this could be populated from an API endpoint
)

if st.sidebar.button("Clear Cache & Refresh Data"):
    st.cache_data.clear()

# --- Data Display ---
col1, col2 = st.columns(2)

with col1:
    st.header(f"📈 Qualified Races (`{analyzer_selection}`)")
    qualified_data, error = get_api_data(f"/api/races/qualified/{analyzer_selection}")

    if error:
        st.error(f"**Failed to fetch qualified races:**\\n\\n{error}")
    elif qualified_data:
        if qualified_data:
            # Corrected to use 'id' instead of 'race_id' to match the Pydantic model
            df = pd.json_normalize(qualified_data, record_path=['runners'], meta=['id', 'venue', 'race_number', 'start_time'])
            st.dataframe(df)
        else:
            st.info(f"No races were qualified by the '{analyzer_selection}' analyzer.")
    else:
        st.info("Awaiting data...")

with col2:
    st.header("📊 Adapter Status")
    status_data, error = get_api_data("/api/adapters/status")

    if error:
        st.error(f"**Failed to fetch adapter status:**\\n\\n{error}")
    elif status_data:
        st.dataframe(pd.DataFrame(status_data))
    else:
        st.info("Awaiting data...")