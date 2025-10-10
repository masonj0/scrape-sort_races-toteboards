import asyncio
import sqlite3
import os
from contextlib import asynccontextmanager
from datetime import date
from typing import List

import aiosqlite
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from python_service.models import AggregatedResponse, Race, TipsheetRace
from python_service.engine import FortunaEngine

# --- Configuration & Initialization ---
DB_PATH = os.getenv("DB_PATH", "fortuna.db")

async def setup_database():
    """Create and populate a temporary database with known data."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tipsheet (
                race_id TEXT PRIMARY KEY,
                track_name TEXT,
                race_number INTEGER,
                post_time TEXT,
                score REAL,
                factors TEXT
            )
        """)
        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup the database on startup
    await setup_database()
    yield
    # Clean up resources on shutdown if needed

app = FastAPI(
    title="Fortuna Faucet API",
    description="Provides access to aggregated and analyzed horse racing data.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow all origins for simplicity in this context
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies ---
def get_current_date() -> date:
    return date.today()

# --- API Endpoints ---
@app.get("/api/races", response_model=AggregatedResponse)
async def get_races_endpoint(request: Request, current_date: date = Depends(get_current_date)):
    fortuna_engine = FortunaEngine()
    background_tasks = request.app.state.background_tasks if hasattr(request.app.state, 'background_tasks') else set()
    response = await fortuna_engine.get_races(date=current_date.isoformat(), background_tasks=background_tasks)
    return response

@app.get("/api/tipsheet", response_model=List[TipsheetRace])
async def get_tipsheet_endpoint(date: date = Depends(get_current_date)):
    """Fetches the generated tipsheet from the database asynchronously."""
    results = []
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM tipsheet WHERE date(post_time) = ? ORDER BY post_time ASC'
            async with db.execute(query, (date.isoformat(),)) as cursor:
                async for row in cursor:
                    results.append(dict(row))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return results