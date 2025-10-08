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

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    app.state.engine = OddsEngine(config=settings)
    app.state.analyzer_engine = AnalyzerEngine()
    log.info("Server startup: OddsEngine initialized.")
    yield
    await app.state.engine.close()
    log.info("Server shutdown: HTTP client resources closed.")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Fortuna Faucet API", version="3.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True, allow_methods=["GET"], allow_headers=["*"]
)

def get_engine(request: Request) -> OddsEngine:
    return request.app.state.engine

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/adapters/status")
@limiter.limit("60/minute")
async def get_all_adapter_statuses(request: Request, engine: OddsEngine = Depends(get_engine), _=Depends(verify_api_key)):
    try:
        return engine.get_all_adapter_statuses()
    except Exception as e:
        log.error("Error in /api/adapters/status", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/races")
@limiter.limit("30/minute")
async def get_races(request: Request, race_date: date = datetime.now().date(), source: str = None, engine: OddsEngine = Depends(get_engine), _=Depends(verify_api_key)):
    try:
        date_str = race_date.strftime('%Y-%m-%d')
        return await engine.fetch_all_odds(date_str, source)
    except Exception as e:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")