# python_service/api.py

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .engine import EngineManager

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan, handling startup and shutdown events.
    """
    logging.info("App startup: Initializing engine and background task.")
    engine = get_engine()
    background_task = asyncio.create_task(engine.run())

    yield  # The application is now running

    logging.info("App shutdown: Cancelling background task and closing resources.")
    background_task.cancel()
    try:
        await background_task
    except asyncio.CancelledError:
        logging.info("Background task successfully cancelled.")

    for adapter in engine.adapters:
        if hasattr(adapter, 'close'):
            await adapter.close()

# --- App Setup ---
app = FastAPI(
    title="Checkmate Ultimate Solo API",
    description="Aggregates horse racing odds from multiple sources.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)

# --- Engine Dependency ---
engine_manager = EngineManager()

def get_engine():
    """Dependency provider for the EngineManager."""
    return engine_manager

# --- API Endpoints ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/races")
async def get_races(engine: EngineManager = Depends(get_engine)):
    """
    Returns the latest fetched race data.
    The engine is injected as a dependency to facilitate testing.
    """
    return engine.last_races