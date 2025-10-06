# python_service/api.py

import structlog
from datetime import datetime, date
from typing import List
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from .config import get_settings
from .engine import OddsEngine
from .models import Race
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
    app.state.engine = OddsEngine(config=settings)
    log.info("Server startup: Configuration validated and OddsEngine initialized.")
    yield
    # Clean up the engine resources
    await app.state.engine.close()
    log.info("Server shutdown: HTTP client resources closed.")

limiter = Limiter(key_func=get_remote_address)

# Pass the lifespan manager to the FastAPI app
app = FastAPI(title="Checkmate Ultimate Solo API", version="2.1", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True, allow_methods=["GET"], allow_headers=["*"]
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
    except Exception as e:
        log.error("Error in /api/adapters/status", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/races/qualified/{analyzer_name}", response_model=List[Race])
@limiter.limit("30/minute")
async def get_qualified_races(
    analyzer_name: str,
    request: Request,
    race_date: date = datetime.now().date(),
    engine: OddsEngine = Depends(get_engine),
    _=Depends(verify_api_key)
):
    """
    Gets all races for a given date, filters them for qualified betting
    opportunities, and returns the qualified races.
    """
    try:
        date_str = race_date.strftime('%Y-%m-%d')
        aggregated_data = await engine.fetch_all_odds(date_str)

        # The engine now correctly returns validated Pydantic models.
        # No re-validation is necessary.
        races = aggregated_data.get('races', [])

        analyzer_engine = AnalyzerEngine()
        # In the future, kwargs could come from the request's query params
        analyzer = analyzer_engine.get_analyzer(analyzer_name)
        qualified_races = analyzer.qualify_races(races)
        return qualified_races
    except ValueError as e:
        # Correctly map a missing analyzer to a 404 Not Found error
        log.warning("Requested analyzer not found", analyzer_name=analyzer_name)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error("Error in /api/races/qualified", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/races")
@limiter.limit("30/minute")
async def get_races(
    request: Request,
    race_date: date = datetime.now().date(),
    source: str = None,
    engine: OddsEngine = Depends(get_engine),
    _=Depends(verify_api_key)
):
    try:
        date_str = race_date.strftime('%Y-%m-%d')
        aggregated_data = await engine.fetch_all_odds(date_str, source)
        return aggregated_data
    except Exception as e:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")