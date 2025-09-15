"""
Checkmate V7: `api.py` - THE CONDUCTOR
"""
from fastapi import FastAPI, BackgroundTasks
from . import services

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Checkmate V7 API is running."}

@app.post("/races/process", status_code=202)
def process_race(race_url: str, background_tasks: BackgroundTasks):
    """Dispatches a background job to process a race."""
    background_tasks.add_task(services.process_race_for_prediction, race_url)
    return {"message": "Race processing job accepted."}
