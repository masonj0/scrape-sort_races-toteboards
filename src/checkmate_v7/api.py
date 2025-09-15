"""
Checkmate V7: `api.py` - THE CONDUCTOR
"""
from fastapi import FastAPI, BackgroundTasks
from . import services, logic
from .models import PerformanceMetricsSchema, ActionStatusSchema, HealthCheckResponse

app = FastAPI(title="Checkmate V7 API")

@app.get("/", tags=["General"])
def read_root():
    return {"status": "ok", "message": "Checkmate V7 API is running."}

@app.get("/health", response_model=HealthCheckResponse, tags=["General"])
def get_health():
    """Returns the health status of the system components."""
    # In a real system, these would be live checks.
    return {
        "status": "ok",
        "database": "ok",
        "celery_status": "ok",
        "active_adapters": ["twinspires_placeholder"]
    }

@app.post("/races/process", response_model=ActionStatusSchema, status_code=202, tags=["Actions"])
def process_race(race_url: str, background_tasks: BackgroundTasks):
    """Dispatches a background job to process a race."""
    background_tasks.add_task(services.process_race_for_prediction, race_url)
    return {"status": "ok", "message": "Race analysis job accepted."}

@app.get("/performance", response_model=PerformanceMetricsSchema, tags=["Performance"])
def get_performance():
    """Returns the system's performance metrics with statistical rigor."""
    # This is a placeholder using dummy data. A real implementation would
    # query the `joins` table from the database.
    dummy_pnl_data = [1.10, -2.0, 1.10, 1.10, -2.0]

    ci = logic.percentile_bootstrap_ci(dummy_pnl_data)
    p_value = logic.wilcoxon_p_value(dummy_pnl_data)

    return {
        "total_bets": 5,
        "total_wins": 3,
        "win_rate_percent": 60.0,
        "total_pnl_usd": sum(dummy_pnl_data),
        "total_staked_usd": 10.0,
        "roi_percent": (sum(dummy_pnl_data) / 10.0) * 100,
        "sample_size": len(dummy_pnl_data),
        "confidence_interval": ci,
        "p_value": p_value
    }
