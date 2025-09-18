import streamlit as st
import pandas as pd
import httpx
from datetime import datetime, timedelta
import asyncio
import pytz

# --- V3 RPB2B Adapter Logic ---
# This section is a simplified, self-contained version of the V3 rpb2b_adapter.
# In the real application, this would be a separate, more robust module.

API_URL = "https://api.beta.racingpost.com/v3/cards"
API_HEADERS = {"X-Api-Key": "23pub-2WqDqDqXp2aA4aB6bC8d"}

async def get_races_from_api(date_str: str, jurisdiction: str = "GB", surface: str = "aw", limit: int = 20):
    """
    Fetches race data from the Racing Post B2B API for a specific date and jurisdiction.
    """
    params = {
        "date": date_str,
        "jurisdiction": jurisdiction,
        "surface": surface,
        "limit": limit,
        "include": "odds"  # Include odds data
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, headers=API_HEADERS, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        st.error(f"API Error: Failed to fetch race data. {e}")
        return []

def parse_races(api_data):
    """
    Parses the raw API data into a more usable list of dictionaries.
    """
    parsed_races = []
    for race_data in api_data:
        # Basic race details
        race = {
            "race_id": race_data.get("id"),
            "track_name": race_data.get("course", {}).get("name"),
            "race_time": race_data.get("raceTime"),
            "race_title": race_data.get("name"),
            "distance_miles_furlongs": race_data.get("distance", {}).get("miles_furlongs"),
            "age_band": race_data.get("ageBand"),
            "race_class": race_data.get("raceClass"),
            "runners": []
        }

        # Runner details
        for runner_data in race_data.get("runners", []):
            runner = {
                "runner_id": runner_data.get("id"),
                "horse_name": runner_data.get("name"),
                "saddle_cloth_number": runner_data.get("saddleClothNumber"),
                "draw": runner_data.get("draw"),
                "jockey_name": runner_data.get("jockey", {}).get("name"),
                "trainer_name": runner_data.get("trainer", {}).get("name"),
                "owner_name": runner_data.get("owner", {}).get("name"),
                "age": runner_data.get("age"),
                "sex": runner_data.get("sex"),
                "odds": "N/A"
            }
            # Find the latest odds from the included odds data
            if "odds" in race_data and race_data["odds"]:
                for odds_entry in race_data["odds"]:
                    if odds_entry.get("runnerId") == runner["runner_id"]:
                        latest_odds = odds_entry.get("latestOdds", [{}])[0]
                        runner["odds"] = latest_odds.get("decimal", "N/A")
                        break
            race["runners"].append(runner)

        parsed_races.append(race)
    return parsed_races

# --- Dynamic Checkmate Scorer ---
# This is a simplified version of the scorer.py module.

def calculate_checkmate_score(runner, race):
    """
    Calculates a 'Checkmate Score' for a runner based on a set of criteria.
    This is a simplified example. A real-world scorer would be more complex.
    """
    score = 0
    # Rule 1: High score for low saddle cloth numbers (potential bias)
    if runner.get("saddle_cloth_number") in [1, 2, 3]:
        score += 25

    # Rule 2: High score for specific jockeys (based on historical performance)
    if runner.get("jockey_name") in ["William Buick", "Ryan Moore", "Frankie Dettori"]:
        score += 30

    # Rule 3: Bonus for favorable draw in smaller fields
    if len(race.get("runners", [])) <= 8 and runner.get("draw", 99) <= 4:
        score += 15

    # Rule 4: Bonus for competitive odds (e.g., between 3.0 and 10.0)
    try:
        odds = float(runner.get("odds", 0))
        if 3.0 <= odds <= 10.0:
            score += 20
    except (ValueError, TypeError):
        pass # Ignore if odds are not a valid number

    # Rule 5: Penalty for very young or very old horses
    if runner.get("age") not in [3, 4, 5]:
        score -= 10

    return max(0, score) # Ensure score is not negative

# --- Streamlit UI ---

st.set_page_config(page_title="Pocket Renaissance", layout="wide")

st.title("Pocket Renaissance: The Checkmate Alert System")
st.write("""
This is a portable demonstration of the "Checkmate Alert System," a real-time tool
for identifying high-potential betting opportunities based on a dynamic scoring model.
""")

# --- Live Monitoring Controls ---
st.sidebar.header("Live Monitoring Controls")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
min_checkmate_score = st.sidebar.slider("Minimum Checkmate Score", 0, 100, 50)

# --- Main Application Logic ---

# Use a session state to store the race data to avoid re-fetching on every interaction
if 'race_data' not in st.session_state:
    st.session_state['race_data'] = []
if 'last_fetch_time' not in st.session_state:
    st.session_state['last_fetch_time'] = datetime.min.replace(tzinfo=pytz.UTC)

# Placeholder for the main race display
placeholder = st.empty()

async def update_race_data():
    """
    Fetches the latest race data from the API and updates the session state.
    """
    utc_now = datetime.now(pytz.UTC)
    # Only fetch if it's been more than the refresh interval since the last fetch
    if (utc_now - st.session_state['last_fetch_time']).total_seconds() > refresh_interval:
        date_str = utc_now.strftime("%Y-%m-%d")
        api_data = await get_races_from_api(date_str)
        if api_data:
            st.session_state['race_data'] = parse_races(api_data)
            st.session_state['last_fetch_time'] = utc_now

async def main():
    """
    The main execution loop for the Streamlit application.
    """
    while True:
        await update_race_data()

        with placeholder.container():
            st.header(f"Race Analysis (Last Updated: {st.session_state['last_fetch_time'].strftime('%Y-%m-%d %H:%M:%S %Z')})")

            if not st.session_state['race_data']:
                st.warning("No race data available. Waiting for the next fetch...")
            else:
                all_runners = []
                for race in st.session_state['race_data']:
                    for runner in race['runners']:
                        score = calculate_checkmate_score(runner, race)
                        if score >= min_checkmate_score:
                            all_runners.append({
                                "Track": race.get("track_name"),
                                "Time": race.get("race_time"),
                                "Race": race.get("race_title"),
                                "Horse": runner.get("horse_name"),
                                "No.": runner.get("saddle_cloth_number"),
                                "Jockey": runner.get("jockey_name"),
                                "Trainer": runner.get("trainer_name"),
                                "Odds": runner.get("odds"),
                                "Checkmate Score": score
                            })

                if all_runners:
                    df = pd.DataFrame(all_runners)
                    df = df.sort_values(by="Checkmate Score", ascending=False)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"No runners meet the minimum Checkmate Score of {min_checkmate_score}.")

        if not auto_refresh:
            break

        await asyncio.sleep(refresh_interval)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
