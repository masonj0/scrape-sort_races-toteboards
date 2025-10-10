# python_service/api.py

import structlog
from datetime import datetime, date
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from datetime import date
from typing import List

from .config import get_settings
from .engine import OddsEngine
from .models import AggregatedResponse, QualifiedRacesResponse
from .security import verify_api_key
from .logging_config import configure_logging
from .analyzer import AnalyzerEngine

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

# Dependency function to get the engine instance from the app state
def get_engine(request: Request) -> OddsEngine:
    return request.app.state.engine

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/adapters/status")
@limiter.limit("60/minute")
async def get_all_adapter_statuses(request: Request, engine: OddsEngine = Depends(get_engine), _=Depends(verify_api_key)):
    """Provides a list of health statuses for all adapters, required by the new frontend blueprint."""
    try:
        statuses = engine.get_all_adapter_statuses()
        return statuses
    except Exception:
        log.error("Error in /api/adapters/status", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/races/qualified/{analyzer_name}", response_model=QualifiedRacesResponse)
@limiter.limit("30/minute")
async def get_qualified_races(
    analyzer_name: str,
    request: Request,
    race_date: Optional[date] = None,
    engine: OddsEngine = Depends(get_engine),
    _=Depends(verify_api_key),
    # --- Dynamic Analyzer Parameters ---
    max_field_size: Optional[int] = Query(None, description="Override the max field size for the analyzer."),
    min_favorite_odds: Optional[float] = Query(None, description="Override the min favorite odds."),
    min_second_favorite_odds: Optional[float] = Query(None, description="Override the min second favorite odds.")
):
    """
    Gets all races for a given date, filters them for qualified betting
    opportunities, and returns the qualified races.
    """
    try:
        if race_date is None:
            race_date = datetime.now().date()
        date_str = race_date.strftime('%Y-%m-%d')
        aggregated_data = await engine.fetch_all_odds(date_str)

        # The engine now correctly returns validated Pydantic models.
        # No re-validation is necessary.
        races = aggregated_data.get('races', [])

        analyzer_engine = request.app.state.analyzer_engine
        # Collect any provided optional parameters into a dictionary
        analyzer_params = {
            "max_field_size": max_field_size,
            "min_favorite_odds": min_favorite_odds,
            "min_second_favorite_odds": min_second_favorite_odds
        }
        # Filter out any parameters that were not provided by the user
        custom_params = {k: v for k, v in analyzer_params.items() if v is not None}

        analyzer = analyzer_engine.get_analyzer(analyzer_name, **custom_params)
        result = analyzer.qualify_races(races)
        return QualifiedRacesResponse(**result)
    except ValueError as e:
        # Correctly map a missing analyzer to a 404 Not Found error
        log.warning("Requested analyzer not found", analyzer_name=analyzer_name)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error("Error in /api/races/qualified", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
        if race_date is None:
            race_date = datetime.now().date()
        date_str = race_date.strftime('%Y-%m-%d')
        aggregated_data = await engine.fetch_all_odds(date_str, source)
        return aggregated_data
    except Exception:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
