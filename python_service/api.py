# python_service/api.py

import logging
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from .config import get_settings
from .engine import OddsEngine
from .security import verify_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define the lifespan context manager for robust startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's lifespan. On startup, it initializes the OddsEngine
    with validated settings and attaches it to the app state. On shutdown, it
    properly closes the engine's resources.
    """
    settings = get_settings()
    app.state.engine = OddsEngine(config=settings)
    logging.info("Server startup: Configuration validated and OddsEngine initialized.")
    yield
    # Clean up the engine resources
    await app.state.engine.close()
    logging.info("Server shutdown: HTTP client resources closed.")

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
        logging.error(f"Error in /api/adapters/status: {e}", exc_info=True)
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
        logging.error(f"Error in /api/races: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")