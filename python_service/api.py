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

from .config import get_settings
from .engine import FortunaEngine
from .models import AggregatedResponse, QualifiedRacesResponse
from .security import verify_api_key
from .logging_config import configure_logging
from .analyzer import AnalyzerEngine

log = structlog.get_logger()

# Define the lifespan context manager for robust startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's lifespan. On startup, it initializes the OddsEngine
    with validated settings and attaches it to the app state. On shutdown, it
    properly closes the engine's resources.
    """
    configure_logging()
    settings = get_settings()
    app.state.engine = FortunaEngine(config=settings)
    app.state.analyzer_engine = AnalyzerEngine()
    log.info("Server startup: Configuration validated and FortunaEngine initialized.")
    yield
    # Clean up the engine resources
    await app.state.engine.close()
    log.info("Server shutdown: HTTP client resources closed.")

limiter = Limiter(key_func=get_remote_address)

# Pass the lifespan manager to the FastAPI app
app = FastAPI(title="Checkmate Ultimate Solo API", version="2.1", lifespan=lifespan)
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True, allow_methods=["GET"], allow_headers=["*"]
)

# Dependency function to get the engine instance from the app state
def get_engine(request: Request) -> FortunaEngine:
    return request.app.state.engine

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/adapters/status")
@limiter.limit("60/minute")
async def get_all_adapter_statuses(request: Request, engine: FortunaEngine = Depends(get_engine), _=Depends(verify_api_key)):
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
    engine: FortunaEngine = Depends(get_engine),
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
        background_tasks = set() # Dummy background tasks
        aggregated_data = await engine.get_races(date_str, background_tasks)

        races = aggregated_data.get('races', [])

        analyzer_engine = request.app.state.analyzer_engine
        analyzer_params = {
            "max_field_size": max_field_size,
            "min_favorite_odds": min_favorite_odds,
            "min_second_favorite_odds": min_second_favorite_odds
        }
        custom_params = {k: v for k, v in analyzer_params.items() if v is not None}

        analyzer = analyzer_engine.get_analyzer(analyzer_name, **custom_params)
        result = analyzer.qualify_races(races)
        return QualifiedRacesResponse(**result)
    except ValueError as e:
        log.warning("Requested analyzer not found", analyzer_name=analyzer_name)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error("Error in /api/races/qualified", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/races", response_model=AggregatedResponse)
@limiter.limit("30/minute")
async def get_races(
    request: Request,
    race_date: Optional[date] = None,
    source: Optional[str] = None,
    engine: FortunaEngine = Depends(get_engine),
    _=Depends(verify_api_key)
):
    try:
        if race_date is None:
            race_date = datetime.now().date()
        date_str = race_date.strftime('%Y-%m-%d')
        background_tasks = set() # Dummy background tasks
        aggregated_data = await engine.get_races(date_str, background_tasks, source)
        return aggregated_data
    except Exception:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
