# python_service/api.py

from contextlib import asynccontextmanager
from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

import aiosqlite
import structlog
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from python_service.middleware.error_handler import ErrorRecoveryMiddleware

from .analyzer import AnalyzerEngine
from .config import get_settings
from .engine import FortunaEngine
from .health import router as health_router
from .logging_config import configure_logging
from .models import AggregatedResponse
from .models import QualifiedRacesResponse
from .models import TipsheetRace
from .security import verify_api_key

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

# Add middlewares (order can be important)
app.add_middleware(ErrorRecoveryMiddleware)
app.include_router(health_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Dependency function to get the engine instance from the app state
def get_engine(request: Request) -> FortunaEngine:
    return request.app.state.engine


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/adapters/status")
@limiter.limit("60/minute")
async def get_all_adapter_statuses(
    request: Request, engine: FortunaEngine = Depends(get_engine), _=Depends(verify_api_key)
):
    """Provides a list of health statuses for all adapters, required by the new frontend blueprint."""
    try:
        statuses = engine.get_all_adapter_statuses()
        return statuses
    except Exception:
        log.error("Error in /api/adapters/status", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(
    "/api/races/qualified/{analyzer_name}",
    response_model=QualifiedRacesResponse,
    description=(
        "Fetch and analyze races from all configured data sources, returning a list of races "
        "that meet the specified analyzer's criteria."
    ),
    responses={
        200: {
            "description": "A list of qualified races with their scores.",
            "content": {
                "application/json": {
                    "example": {
                        "races": [
                            {
                                "id": "12345_2025-10-14_1",
                                "venue": "Santa Anita",
                                "race_number": 1,
                                "start_time": "2025-10-14T20:30:00Z",
                                "runners": [{"number": 1, "name": "Speedy Gonzalez", "odds": "5/2"}],
                                "source": "TVG",
                                "qualification_score": 95.5,
                            }
                        ],
                        "analyzer": "trifecta_analyzer",
                    }
                }
            },
        },
        404: {"description": "The specified analyzer was not found."},
    },
)
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
    min_second_favorite_odds: Optional[float] = Query(None, description="Override the min second favorite odds."),
):
    """
    Gets all races for a given date, filters them for qualified betting
    opportunities, and returns the qualified races.
    """
    try:
        if race_date is None:
            race_date = datetime.now().date()
        date_str = race_date.strftime("%Y-%m-%d")
        background_tasks = set()  # Dummy background tasks
        aggregated_data = await engine.get_races(date_str, background_tasks)

        races = aggregated_data.get("races", [])

        analyzer_engine = request.app.state.analyzer_engine
        analyzer_params = {
            "max_field_size": max_field_size,
            "min_favorite_odds": min_favorite_odds,
            "min_second_favorite_odds": min_second_favorite_odds,
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
    _=Depends(verify_api_key),
):
    try:
        if race_date is None:
            race_date = datetime.now().date()
        date_str = race_date.strftime("%Y-%m-%d")
        background_tasks = set()  # Dummy background tasks
        aggregated_data = await engine.get_races(date_str, background_tasks, source)
        return aggregated_data
    except Exception:
        log.error("Error in /api/races", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


DB_PATH = "fortuna.db"


def get_current_date() -> date:
    return datetime.now().date()


@app.get("/api/tipsheet", response_model=List[TipsheetRace])
@limiter.limit("30/minute")
async def get_tipsheet_endpoint(request: Request, date: date = Depends(get_current_date)):
    """Fetches the generated tipsheet from the database asynchronously."""
    results = []
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM tipsheet WHERE date(post_time) = ? ORDER BY post_time ASC"
            async with db.execute(query, (date.isoformat(),)) as cursor:
                async for row in cursor:
                    results.append(dict(row))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return results
