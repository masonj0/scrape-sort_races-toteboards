# src/paddock_parser/api/main.py

import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Response
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

@app.get("/api/v1/races.json", response_model=List[RaceSchema], include_in_schema=False)
async def get_races_json(min_runners: Optional[int] = None, source: Optional[str] = None):
    """
    Alias for /api/v1/races. Returns race data in JSON format.
    """
    return await get_races(min_runners=min_runners, source=source)


@app.get("/api/v1/races.csv")
async def get_races_csv(min_runners: Optional[int] = None, source: Optional[str] = None):
    """
    Retrieves a list of races from the pipeline and returns it as a CSV file.
    The nested runner data is not included in the CSV output.
    """
    races = await run_pipeline(min_runners=min_runners, specific_source=source)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = ["race_id", "track_name", "race_number", "post_time", "number_of_runners", "score"]
    writer.writerow(header)

    # Write data rows
    for race in races:
        writer.writerow([
            race.race_id,
            race.track_name,
            race.race_number,
            race.post_time.isoformat(),
            race.number_of_runners,
            race.score
        ])

    return Response(content=output.getvalue(), media_type="text/csv")
