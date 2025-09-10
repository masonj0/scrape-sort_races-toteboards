"""
Paddock Parser NG - Portable Checkmate Demo

This script is a self-contained demonstration of the "Checkmate Alert System".
It encapsulates the essential logic from the main application, focusing on the
rpb2b.com API as the sole data source.

Required Dependencies:
- streamlit
- httpx

How to Run:
1. Make sure you have the required dependencies installed:
   pip install streamlit httpx
2. Run the script from your terminal:
   streamlit run portable_demo.py
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional

import httpx
import streamlit as st

# --- "The Guardian" (Models) ---

@dataclass
class NormalizedRunner:
    name: str
    program_number: int
    odds: Optional[float] = None
    scratched: bool = False
    jockey: Optional[str] = None
    trainer: Optional[str] = None

@dataclass
class NormalizedRace:
    race_id: str
    track_name: str
    race_number: int
    post_time: Optional[datetime] = None
    race_type: Optional[str] = None
    minutes_to_post: Optional[int] = None
    number_of_runners: Optional[int] = None
    score: Optional[float] = None
    scores: Dict[str, float] = field(default_factory=dict)
    runners: List[NormalizedRunner] = field(default_factory=list)

# --- "The Template" (Adapter Logic) ---

BASE_URL = "https://backend-us-racecards.widget.rpb2b.com/v2"

def _convert_odds_to_float(odds_str: Optional[str]) -> Optional[float]:
    if not odds_str or not isinstance(odds_str, str):
        return None
    odds_str = odds_str.strip().upper()
    if "SP" in odds_str:
        return None
    if "/" in odds_str:
        try:
            num, den = map(int, odds_str.split("/"))
            return (num / den) + 1.0 if den != 0 else None
        except (ValueError, ZeroDivisionError):
            return None
    return None

def _parse_race(race_detail: Dict, race_id: str, track_name: str) -> Optional[NormalizedRace]:
    try:
        runners = [
            NormalizedRunner(
                name=runner_data.get("horseId"),
                odds=_convert_odds_to_float(runner_data.get("startingPrice")),
                program_number=runner_data.get("draw"),
            )
            for runner_data in race_detail.get("results", {}).get("result", [])
        ]

        post_time_str = race_detail.get("datetimeUtc")
        post_time = datetime.fromisoformat(post_time_str) if post_time_str else None

        return NormalizedRace(
            race_id=race_id,
            track_name=track_name,
            race_number=race_detail.get("raceNumber"),
            race_type=race_detail.get("raceType"),
            number_of_runners=race_detail.get("numberOfRunners"),
            post_time=post_time,
            runners=runners,
        )
    except (KeyError, TypeError):
        return None

async def fetch_rpb2b_data(race_ids: Optional[List[str]] = None) -> List[NormalizedRace]:
    race_id_to_track_map = {}
    if not race_ids:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        index_url = f"{BASE_URL}/racecards/daily/{today}"
        async with httpx.AsyncClient() as client:
            response = await client.get(index_url)
        race_list = response.json()
        race_id_to_track_map = {
            race["id"]: course.get("name", "Unknown")
            for course in race_list for race in course.get("races", [])
        }
        race_ids = list(race_id_to_track_map.keys())

    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"{BASE_URL}/racecards/{race_id}?include=odds") for race_id in race_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    all_races = []
    for response, race_id in zip(responses, race_ids):
        if isinstance(response, Exception):
            continue
        race_detail = response.json()
        track_name = race_id_to_track_map.get(race_id, "Unknown")
        race = _parse_race(race_detail, race_id, track_name)
        if race:
            all_races.append(race)
    return all_races

# --- "The Brain" (Scorer Logic) ---

def _get_dynamic_odds_thresholds(field_size: int) -> Dict[str, float]:
    if field_size >= 7: return {"fav": 1.0, "second_fav": 4.0}
    if field_size == 6: return {"fav": 1.0, "second_fav": 3.5}
    if field_size == 5: return {"fav": 0.8, "second_fav": 3.0}
    if field_size == 4: return {"fav": 0.5, "second_fav": 2.0}
    return {"fav": 0.0, "second_fav": 0.0}

def find_checkmate_opportunities(races: List[NormalizedRace]) -> List[NormalizedRace]:
    checkmate_races = []
    for race in races:
        if not race.runners or not race.number_of_runners: continue
        thresholds = _get_dynamic_odds_thresholds(race.number_of_runners)
        sorted_runners = sorted(race.runners, key=lambda r: r.odds or float('inf'))
        if len(sorted_runners) < 2: continue

        fav_odds = sorted_runners[0].odds or 0.0
        second_fav_odds = sorted_runners[1].odds or 0.0

        if fav_odds > thresholds["fav"] and second_fav_odds > thresholds["second_fav"]:
            checkmate_races.append(race)
    return checkmate_races

# --- "The Face" (Dashboard Logic) ---

st.set_page_config(layout="wide")
st.title("Portable Checkmate Alert System")

if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'daily_races' not in st.session_state:
    st.session_state.daily_races = []
if 'last_full_fetch' not in st.session_state:
    st.session_state.last_full_fetch = None

if st.button("Start Monitoring", type="primary"):
    st.session_state.monitoring = True
    st.session_state.last_full_fetch = None
    st.experimental_rerun()

if st.button("Stop Monitoring"):
    st.session_state.monitoring = False
    st.experimental_rerun()

if st.session_state.monitoring:
    st.success("Monitoring for Checkmate opportunities...")

    placeholder = st.empty()

    while st.session_state.monitoring:
        now = datetime.now(UTC)

        if (st.session_state.last_full_fetch is None or
            (now - st.session_state.last_full_fetch) > timedelta(minutes=15)):
            with st.spinner("Performing full daily race refresh..."):
                st.session_state.daily_races = asyncio.run(fetch_rpb2b_data())
                st.session_state.last_full_fetch = now

        with placeholder.container():
            imminent_races = [
                r for r in st.session_state.daily_races
                if r.post_time and (now - timedelta(minutes=1)) < r.post_time <= (now + timedelta(minutes=5))
            ]

            if imminent_races:
                live_races = asyncio.run(fetch_rpb2b_data(race_ids=[r.race_id for r in imminent_races]))
                checkmate_races = find_checkmate_opportunities(live_races)

                if checkmate_races:
                    for race in checkmate_races:
                        st.toast(f"🚨 CHECKMATE! {race.track_name} - Race {race.race_number}")
                        st.write(f"🚨 CHECKMATE! {race.track_name} - Race {race.race_number}")

            st.write(f"Last check: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        time.sleep(60)
        st.experimental_rerun()
else:
    st.info("Monitoring is stopped.")
