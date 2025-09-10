#!/usr/bin/env python3
"""
Portable Demo: The T-G-H Showcase
A single-file Streamlit application to showcase Thoroughbred, Greyhound, and Harness racing data.
To run:
1. Ensure you have dependencies: streamlit, httpx, pandas, beautifulsoup4
2. From your terminal, run: streamlit run portable_demo.py
"""

import asyncio
import streamlit as st
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, UTC
import httpx
import pandas as pd
from io import StringIO
import json

#
# --- PILLAR 2: THE GUARDIAN (Data Models) ---
#

@dataclass
class NormalizedRunner:
    """A simple dataclass for a runner with its odds."""
    name: str
    odds: float = 0.0

@dataclass
class NormalizedRace:
    """A simple dataclass for a race, containing its runners."""
    track: str
    race_number: int
    race_time: datetime = None
    discipline: str = "Thoroughbred"
    runners: list[NormalizedRunner] = field(default_factory=list)

#
# --- PILLAR 3: THE BRAIN (Scoring Logic) ---
#

def get_dynamic_odds_thresholds(field_size: int) -> tuple[float, float]:
    """Returns (fav_threshold, second_fav_threshold) based on field size."""
    if field_size <= 4:
        return (0.5, 2.0)
    if field_size == 5:
        return (0.8, 3.0)
    if field_size == 6:
        return (1.0, 3.5)
    return (1.0, 4.0)  # Default for 7 or more

def find_checkmate_opportunities(races: list[NormalizedRace]) -> list[NormalizedRace]:
    """Applies the dynamic 'Checkmate' filter to a list of races."""
    opportunities = []
    for race in races:
        if not race.runners or len(race.runners) < 2:
            continue

        sorted_runners = sorted(race.runners, key=lambda r: r.odds)
        field_size = len(sorted_runners)

        if field_size >= 7:
            continue

        fav_threshold, second_fav_threshold = get_dynamic_odds_thresholds(field_size)

        favorite = sorted_runners[0]
        second_favorite = sorted_runners[1]

        if favorite.odds > fav_threshold and second_favorite.odds > second_fav_threshold:
            opportunities.append(race)

    return opportunities

#
# --- PILLAR 1: THE TEMPLATE (Adapter Logic) ---
#

async def fetch_rpb2b_data() -> list[NormalizedRace]:
    """Fetches and parses live race data from the RPB2B API."""
    BASE_URL = "https://backend-us-racecards.widget.rpb2b.com/v2"
    all_races = []
    date_str = datetime.now().strftime('%Y-%m-%d')
    daily_url = f"{BASE_URL}/racecards/daily/{date_str}"

    headers = {"Accept": "application/json", "Referer": "https://widget.rpb2b.com/"}

    async with httpx.AsyncClient(headers=headers) as client:
        try:
            daily_response = await client.get(daily_url, timeout=20.0)
            daily_response.raise_for_status()
            daily_data = daily_response.json()
            race_ids = [race['id'] for course in daily_data.get('courses', []) for race in course.get('races', [])]

            tasks = [client.get(f"{BASE_URL}/racecards/{race_id}?include=odds", timeout=20.0) for race_id in race_ids]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for response in responses:
                if isinstance(response, httpx.Response) and response.status_code == 200:
                    race_data = response.json()
                    runners = []
                    for runner_data in race_data.get('runners', []):
                        try:
                            odds_decimal = runner_data.get('odds', {}).get('decimal')
                            if odds_decimal:
                                runners.append(NormalizedRunner(name=runner_data.get('name'), odds=float(odds_decimal)))
                        except (ValueError, TypeError):
                            continue

                    if runners:
                        all_races.append(NormalizedRace(
                            track=race_data.get('course', {}).get('name', 'Unknown'),
                            race_number=race_data.get('raceNumber', 0),
                            race_time=datetime.fromisoformat(race_data.get('startTime')),
                            runners=runners
                        ))
        except httpx.HTTPStatusError as e:
            st.error(f"API Error: Failed to fetch data. Status code: {e.response.status_code}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    return all_races

async def fetch_iggy_joey_data() -> pd.DataFrame:
    """Fetches and parses data from the Betfair Data Scientist API (Iggy-Joey model)."""
    BASE_URL = "https://betfair-data-supplier.herokuapp.com/api/widgets/iggy-joey/datasets"
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/?date={today}&presenter=RatingsPresenter&csv=true"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            csv_data = response.text
            if not csv_data:
                return pd.DataFrame()

            data = StringIO(csv_data)
            df = pd.read_csv(data)
            df.rename(columns={"meetings.races.runners.ratedPrice": "rating"}, inplace=True)
            return df[["market_id", "selection_id", "rating"]]
        except httpx.HTTPStatusError as e:
            st.error(f"API Error: Failed to fetch greyhound data. Status code: {e.response.status_code}")
        except Exception as e:
            st.error(f"An unexpected error occurred while fetching greyhound data: {e}")
    return pd.DataFrame()

async def fetch_harness_data() -> list[NormalizedRace]:
    """Fetches and parses harness racing data from the Racing and Sports API."""
    BASE_URL = "https://www.racingandsports.com.au/todays-racing-json-v2"
    harness_races = []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, timeout=30.0)
            response.raise_for_status()
            json_data = response.json()

            for discipline_group in json_data or []:
                if "harness" in (discipline_group.get("DisciplineFullText") or "").lower():
                    for country_group in discipline_group.get("Countries", []):
                        for meeting in country_group.get("Meetings", []):
                            harness_races.append(NormalizedRace(
                                track=meeting.get("Course", "Unknown"),
                                race_number=meeting.get("RaceNumber", 0),
                                discipline="Harness"
                            ))
        except httpx.HTTPStatusError as e:
            st.error(f"API Error: Failed to fetch harness data. Status code: {e.response.status_code}")
        except Exception as e:
            st.error(f"An unexpected error occurred while fetching harness data: {e}")

    return harness_races

#
# --- PILLAR 4: THE FACE (Streamlit Dashboard UI) ---
#

def display_header():
    """Displays the main header and introductory text."""
    st.title("🏇 T-G-H Showcase")
    st.write("""
        This tool showcases data from three different racing disciplines:
        Thoroughbreds, Greyhounds, and Harness racing.
    """)

def run_monitoring_loop():
    """The main monitoring and display loop for the Streamlit app."""
    placeholder = st.empty()

    while st.session_state.get("monitoring", False):
        with placeholder.container():
            current_time_str = datetime.now().strftime('%H:%M:%S')
            st.info(f"Scanning for opportunities... Last update: {current_time_str}")

            all_races = asyncio.run(fetch_rpb2b_data())

            if not all_races:
                st.warning("No race data could be fetched. The source may be unavailable.")
                time.sleep(60)
                continue

            now = datetime.utcnow()
            upcoming_races = [
                race for race in all_races
                if race.race_time.replace(tzinfo=None) > now and race.race_time.replace(tzinfo=None) - now < timedelta(minutes=30)
            ]

            opportunities = find_checkmate_opportunities(upcoming_races)

            st.subheader("Checkmate Opportunities (Next 30 Mins)")
            if opportunities:
                st.dataframe(opportunities)
                for race in opportunities:
                    mtp = (race.race_time.replace(tzinfo=None) - now).seconds // 60
                    if mtp <= 1:
                        st.toast(f"🚨 CHECKMATE! {race.track} R{race.race_number} at {mtp} MTP!", icon="🚨")
            else:
                st.write("No Checkmate opportunities found in the current upcoming races.")

        time.sleep(60)

    st.info("Monitoring stopped.")

def main():
    """Main function to run the Streamlit application."""
    display_header()

    thoroughbred_tab, greyhound_tab, harness_tab = st.tabs(["Thoroughbreds", "Greyhounds", "Harness"])

    with thoroughbred_tab:
        st.header("Thoroughbred Checkmate Alerts")
        if "monitoring" not in st.session_state:
            st.session_state.monitoring = False

        def start_monitoring():
            st.session_state.monitoring = True

        def stop_monitoring():
            st.session_state.monitoring = False

        if st.session_state.monitoring:
            st.button("Stop Monitoring", on_click=stop_monitoring, type="primary")
            run_monitoring_loop()
        else:
            st.button("Start Monitoring", on_click=start_monitoring)

    with greyhound_tab:
        st.header("Greyhound Predictive Ratings")
        if st.button("Fetch Greyhound Ratings"):
            with st.spinner("Fetching data from Betfair..."):
                ratings_df = asyncio.run(fetch_iggy_joey_data())
                if not ratings_df.empty:
                    st.dataframe(ratings_df)
                else:
                    st.warning("No greyhound ratings data available.")

    with harness_tab:
        st.header("Harness Racing Today")
        if st.button("Fetch Harness Races"):
            with st.spinner("Fetching data from Racing and Sports..."):
                harness_races = asyncio.run(fetch_harness_data())
                if harness_races:
                    st.dataframe([asdict(r) for r in harness_races])
                else:
                    st.warning("No harness racing data available.")


if __name__ == "__main__":
    main()
