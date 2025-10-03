# python_service/api.py

import logging
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .engine import OddsEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Checkmate Ultimate Solo API", version="2.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True, allow_methods=["GET"], allow_headers=["*"]
)

engine: OddsEngine

@app.on_event("startup")
async def startup_event():
    global engine
    engine = OddsEngine()

@app.on_event("shutdown")
async def shutdown_event():
    await engine.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/races")
@limiter.limit("30/minute") # Apply rate limit
async def get_races(request: Request, race_date: date = datetime.now().date(), source: str = None):
    try:
        date_str = race_date.strftime('%Y-%m-%d')
        aggregated_data = await engine.fetch_all_odds(date_str, source)
        return aggregated_data
    except Exception as e:
        logging.error(f"Error in /api/races: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")