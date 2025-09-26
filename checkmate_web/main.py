# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import logging

from engine import DataSourceOrchestrator, TrifectaAnalyzer, Settings, Race, RaceDataSchema, HorseSchema

app = FastAPI(title="Checkmate Live Racing Analysis")
app.mount("/static", StaticFiles(directory="static"), name="static")

CACHE = {
    "last_update": None, "races": [], "adapter_status": [],
    "analysis_results": [], "is_fetching": False
}
settings = Settings()
orchestrator = DataSourceOrchestrator()
analyzer = TrifectaAnalyzer()

def convert_race_to_schema(race: Race) -> RaceDataSchema:
    horses = [HorseSchema(name=r.name, number=r.program_number, odds=r.odds) for r in race.runners if r.odds is not None]
    return RaceDataSchema(id=race.race_id, track=race.track_name, raceNumber=race.race_number, postTime=race.post_time.isoformat() if race.post_time else None, horses=horses)

async def fetch_and_analyze_races():
    if CACHE["is_fetching"]: return
    CACHE["is_fetching"] = True
    try:
        raw_races, adapter_statuses = orchestrator.get_races()
        CACHE["races"] = raw_races
        CACHE["adapter_status"] = adapter_statuses

        analysis_results = []
        for race in raw_races:
            race_schema = convert_race_to_schema(race)
            # Use the single, global settings instance for analysis
            analysis = analyzer.analyze_race(race_schema, settings)
            analysis_results.append({
                "race_id": race.race_id, "track_name": race.track_name, "race_number": race.race_number,
                "post_time": race.post_time.isoformat() if race.post_time else None,
                "runners": [{"name": r.name, "odds": r.odds, "number": r.program_number} for r in race.runners],
                "qualified": analysis["qualified"], "checkmate_score": analysis["checkmateScore"],
                "trifecta_factors": analysis.get("trifectaFactors", {}), "source": getattr(race, 'source', 'unknown')
            })
        CACHE["analysis_results"] = analysis_results
        CACHE["last_update"] = datetime.now().isoformat()
    finally:
        CACHE["is_fetching"] = False

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_and_analyze_races())

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r") as f: return HTMLResponse(content=f.read())

@app.get("/api/status")
async def get_system_status():
    return {
        "status": "online",
        "is_fetching": CACHE["is_fetching"], "last_update": CACHE["last_update"],
        "races_count": len(CACHE["races"]),
        "qualified_count": len([r for r in CACHE["analysis_results"] if r["qualified"]])
    }

@app.get("/api/races/all")
async def get_all_races():
    return {"races": CACHE["analysis_results"], "last_update": CACHE["last_update"]}

@app.get("/api/races/qualified")
async def get_qualified_races():
    qualified = [r for r in CACHE["analysis_results"] if r["qualified"]]
    return {"qualified_races": qualified, "count": len(qualified), "last_update": CACHE["last_update"]}

@app.get("/api/adapters/status")
async def get_adapter_status():
    return {"adapters": CACHE["adapter_status"], "timestamp": datetime.now().isoformat()}

@app.post("/api/refresh")
async def trigger_refresh(background_tasks: BackgroundTasks):
    if CACHE["is_fetching"]: raise HTTPException(status_code=409, detail="Already fetching data")
    background_tasks.add_task(fetch_and_analyze_races)
    return {"status": "refresh_started"}

@app.get("/api/settings")
async def get_settings():
    return settings.model_dump()

@app.post("/api/settings")
async def update_settings(new_settings: Dict):
    try:
        for key, value in new_settings.items():
            if hasattr(settings, key.upper()):
                setattr(settings, key.upper(), value)
        # After updating settings, re-analyze existing data
        asyncio.create_task(fetch_and_analyze_races())
        return {"status": "settings_updated", "settings": settings.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "adapters_count": len(orchestrator.adapters),
        "last_successful_fetch": CACHE.get("last_update")
    }