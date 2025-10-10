# python_service/api.py

import asyncio
from datetime import date
from typing import List

import aiosqlite
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# CRITICAL FIX (BUG #2): Add all required slowapi imports
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from python_service.models import AggregatedResponse, Race, TipsheetRace
from python_service.engine import FortunaEngine

# --- Configuration & Initialization ---
DB_PATH = 'fortuna.db'

# CRITICAL FIX (BUG #2): Correctly instantiate the limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Fortuna Faucet API",
    description="Provides access to aggregated and analyzed horse racing data.",
    version="1.0.0",
)

# CRITICAL FIX (BUG #2): Add limiter state and exception handler to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"error": f"Rate limit exceeded: {exc.detail}"}
))

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
@limiter.limit("10/minute")
async def get_races_endpoint(request: Request, current_date: date = Depends(get_current_date)):
    fortuna_engine = FortunaEngine()
    background_tasks = request.app.state.background_tasks
    response = await fortuna_engine.get_races(date=current_date.isoformat(), background_tasks=background_tasks)
    return response

@app.get("/api/tipsheet", response_model=List[TipsheetRace])
@limiter.limit("30/minute")
async def get_tipsheet_endpoint(request: Request, date: date = Depends(get_current_date)):
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

@app.on_event("startup")
async def startup_event():
    app.state.background_tasks = set()
