#!/usr/bin/env python3
"""
The One Script: The Complete Paddock Parser "Modern Renaissance"
A single, self-contained application for finding real-time "Checkmate" betting opportunities.
Powered by The Racing API.

Setup:
1. Create a file named .env in this directory.
2. Add your API key to it: RACING_API_KEY="YOUR_KEY"
3. Run: pip install streamlit httpx python-dotenv
4. Execute: streamlit run the_one_script.py
"""

import asyncio
import streamlit as st
import time
import os
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import httpx
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv()
API_KEY = os.getenv("RACING_API_KEY")
BASE_URL = "https://api.theracingapi.com/v1"

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
    race_time: datetime
    runners: list[NormalizedRunner] = field(default_factory=list)

#
# --- PILLAR 1: THE TEMPLATE (The One Adapter) ---
#

async def fetch_racing_api_data(fetch_date: date) -> list[NormalizedRace]:
    """Fetches and parses race data from The Racing API."""
    if not API_KEY:
        st.error("RACING_API_KEY not found in .env file. Please create the file and add your key.")
        return []

    url = f"{BASE_URL}/racecards"
    params = {
        "api_key": API_KEY,
        "date": fetch_date.strftime('%Y-%m-%d'),
        "region": "USA"
    }
    all_races = []

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            json_content = response.json()

            for race in json_content.get('racecards', []):
                try:
                    runners = []
                    for horse in race.get('runners', []):
                        odds = horse.get('odds', {}).get('decimal')
                        if odds:
                            runners.append(NormalizedRunner(name=horse.get('name'), odds=float(odds)))

                    if runners:
                        all_races.append(NormalizedRace(
                            track=race.get('course'),
                            race_number=int(race.get('race_num')),
                            race_time=datetime.fromisoformat(race.get('off_time')),
                            runners=runners
                        ))
                except Exception as e:
                    st.warning(f"Skipping a malformed race: {e}")
                    continue
        except httpx.HTTPStatusError as e:
            st.error(f"API Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            
    return all_races

#
# --- PILLAR 3: THE BRAIN (The Checkmate Scorer) ---
#

def get_dynamic_odds_thresholds(field_size: int) -> tuple[float, float]:
    """Returns (fav_threshold, second_fav_threshold) based on field size."""
    if field_size <= 4: return (0.5, 2.0)
    if field_size == 5: return (0.8, 3.0)
    if field_size == 6: return (1.0, 3.5)
    return (1.0, 4.0)

def find_checkmate_opportunities(races: list[NormalizedRace]) -> list[NormalizedRace]:
    """Applies the dynamic 'Checkmate' filter to a list of races."""
    opportunities = []
    for race in races:
        if not race.runners or len(race.runners) < 2 or len(race.runners) >= 7:
            continue

        sorted_runners = sorted(race.runners, key=lambda r: r.odds)
        field_size = len(sorted_runners)
        fav_threshold, second_fav_threshold = get_dynamic_odds_thresholds(field_size)
        
        favorite = sorted_runners[0]
        second_favorite = sorted_runners[1]

        if favorite.odds > fav_threshold and second_favorite.odds > second_fav_threshold:
            opportunities.append(race)
            
    return opportunities

#
# --- PILLAR 4: THE FACE (The Live Dashboard) ---
#

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Checkmate Alert System", layout="wide")
    st.title("🏇 Checkmate Alert System")
    st.write("Live monitoring for US Thoroughbred races using The Racing API.")

    if not API_KEY:
        st.error("API Key is missing. Please set up your .env file.")
        return

    if "monitoring" not in st.session_state:
        st.session_state.monitoring = False

    def toggle_monitoring():
        st.session_state.monitoring = not st.session_state.monitoring

    button_text = "Stop Monitoring" if st.session_state.monitoring else "Start Monitoring"
    st.button(button_text, on_click=toggle_monitoring)

    if st.session_state.monitoring:
        placeholder = st.empty()
        while st.session_state.monitoring:
            with placeholder.container():
                current_time_str = datetime.now().strftime('%H:%M:%S')
                st.info(f"Scanning for opportunities... Last update: {current_time_str}")

                all_races = asyncio.run(fetch_racing_api_data(date.today()))
                
                if not all_races:
                    st.warning("No race data could be fetched. Waiting for the next cycle.")
                    time.sleep(60)
                    continue

                now = datetime.utcnow()
                upcoming_races = [
                    race for race in all_races 
                    if race.race_time > now and race.race_time - now < timedelta(minutes=30)
                ]
                
                opportunities = find_checkmate_opportunities(upcoming_races)

                st.subheader("Checkmate Opportunities (Next 30 Mins)")
                if opportunities:
                    st.dataframe(opportunities)
                    for race in opportunities:
                        mtp = (race.race_time - now).seconds // 60
                        if mtp <= 1:
                            st.toast(f"🚨 CHECKMATE! {race.track} R{race.race_number} at {mtp} MTP!", icon="🚨")
                else:
                    st.write("No Checkmate opportunities found in the current upcoming races.")
            
            time.sleep(60)
        st.success("Monitoring stopped.")

if __name__ == "__main__":
    main()