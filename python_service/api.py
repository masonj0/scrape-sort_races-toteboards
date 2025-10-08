# python_service/api.py

import structlog
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from .config import get_settings
from .orchestrator import fetch_all_races, get_adapter_statuses
from .models import Race, RaceDay
from .security import verify_api_key
from .logging_config import configure_logging
from .analyzer import AnalyzerEngine

log = structlog.get_logger()
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's lifespan. On startup, it initializes the AnalyzerEngine
    and attaches it to the app state.
    """
    app.state.analyzer_engine = AnalyzerEngine()
    log.info("Server startup: AnalyzerEngine initialized.")
    yield
    log.info("Server shutdown.")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Fortuna Faucet V4 - Unified Architecture",
    version="4.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/adapters/status")
@limiter.limit("60/minute")
async def get_all_adapter_statuses(request: Request, _=Depends(verify_api_key)):
    return get_adapter_statuses()

@app.get("/api/races", response_model=List[RaceDay])
@limiter.limit("30/minute")
async def get_races(request: Request, _=Depends(verify_api_key)):
    try:
        return await fetch_all_races()
    except Exception:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/races/qualified/{analyzer_name}", response_model=List[Race])
@limiter.limit("30/minute")
async def get_qualified_races(
    analyzer_name: str,
    request: Request,
    _=Depends(verify_api_key)
):
    """
    Gets all races for the day, filters them using the specified analyzer,
    and returns the qualified races.
    """
    try:
        race_days = await fetch_all_races()
        all_races: List[Race] = [race for day in race_days for race in day.races]

        analyzer_engine = request.app.state.analyzer_engine
        analyzer = analyzer_engine.get_analyzer(analyzer_name)
        qualified_races = analyzer.qualify_races(all_races)
        return qualified_races
    except ValueError as e:
        log.warning("Requested analyzer not found", analyzer_name=analyzer_name)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log.error("Error in /api/races/qualified", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")