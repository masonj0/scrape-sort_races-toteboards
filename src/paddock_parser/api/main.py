# src/paddock_parser/api/main.py

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

# The core logic of our application is in the pipeline
from src.paddock_parser.pipeline import run_pipeline

# Pydantic Models (Schemas) for the API response.
# These will ensure the output is validated and serialized correctly.
# The 'from_attributes=True' mode (via ConfigDict) allows creating these
# models directly from our existing dataclasses (e.g., NormalizedRace).

class RunnerSchema(BaseModel):
    """Pydantic schema for a single runner."""
    model_config = ConfigDict(from_attributes=True)

    name: str
    program_number: int


class RaceSchema(BaseModel):
    """Pydantic schema for a single race, including a list of runners."""
    model_config = ConfigDict(from_attributes=True)

    race_id: str
    track_name: str
    race_number: int
    post_time: datetime
    number_of_runners: int
    runners: List[RunnerSchema]
    score: int


# Create the FastAPI application instance
app = FastAPI()


@app.get("/")
def read_root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "Paddock Parser API is running."}


@app.get("/api/v1/races", response_model=List[RaceSchema])
async def get_races(min_runners: Optional[int] = None, source: Optional[str] = None):
    """
    Retrieves a list of races from the pipeline, optionally filtered by the
    minimum number of runners or a specific data source.
    """
    # The API exposes 'source' as the query parameter for user convenience,
    # but the underlying pipeline function expects 'specific_source'.
    # We perform the mapping here.
    races = await run_pipeline(min_runners=min_runners, specific_source=source)
    return races
