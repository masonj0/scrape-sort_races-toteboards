"""
Checkmate V7: `api.py` - THE CONDUCTOR
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from . import services
import numpy as np
from scipy.stats import wilcoxon

def percentile_bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    """Calculate percentile bootstrap confidence interval for the mean."""
    if len(data) < 2:
        return (np.nan, np.nan)
    bootstrap_means = []
    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))

    lower_bound = np.percentile(bootstrap_means, (1 - ci_level) / 2 * 100)
    upper_bound = np.percentile(bootstrap_means, (1 + ci_level) / 2 * 100)
    return (lower_bound, upper_bound)

def wilcoxon_p_value(data):
    """Perform a one-sample Wilcoxon signed-rank test."""
    if len(data) < 10: # Not enough data for a meaningful test
        return np.nan
    # Test if the mean of the data is significantly different from zero
    statistic, p_value = wilcoxon(data)
    return p_value

from . import logging_config

app = FastAPI()

@app.on_event("startup")
def on_startup():
    """
    Configures logging and overrides Uvicorn's default loggers
    to use the new structured JSON format on application startup.
    """
    logging_config.setup_logging()

    # Reconfigure Uvicorn's loggers to use our new handler
    # This ensures that access logs and server errors are also in JSON format
    loggers_to_override = ["uvicorn", "uvicorn.error", "uvicorn.access"]
    root_handlers = logging.getLogger().handlers

    for logger_name in loggers_to_override:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = root_handlers
        uvicorn_logger.propagate = False

@app.get("/")
def root():
    return {"message": "Checkmate V7 API is running."}

@app.post("/races/process", status_code=202)
def process_race(race_url: str, background_tasks: BackgroundTasks):
    """Dispatches a background job to process a race."""
    background_tasks.add_task(services.process_race_for_prediction, race_url)
    return {"message": "Race processing job accepted."}

from .models import PerformanceMetricsSchema, JoinORM, PredictionORM, PredictionSchema
from .services import get_db_session

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging
from typing import List
from datetime import datetime, timezone

@app.get("/predictions/active", response_model=List[PredictionSchema])
def get_active_predictions():
    """Returns all predictions with a 'pending' status."""
    session = get_db_session()
    try:
        pending_preds = session.query(PredictionORM).filter(PredictionORM.status == 'pending').all()

        results = []
        for pred in pending_preds:
            pred_schema = PredictionSchema.from_orm(pred)
            if pred.race_local_datetime:
                # Assume race_local_datetime is a naive datetime representing UTC
                post_time_utc = pred.race_local_datetime.replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                minutes_to_post = (post_time_utc - now_utc).total_seconds() / 60
                pred_schema.minutes_to_post = minutes_to_post
            results.append(pred_schema)

        return results
    except SQLAlchemyError as e:
        logging.error("Database error while fetching active predictions", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logging.error("An unexpected error occurred while fetching active predictions", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if session:
            session.close()

@app.get("/performance", response_model=PerformanceMetricsSchema)
def get_performance():
    """Returns a statistically rigorous performance report."""
    session = get_db_session()
    try:
        joins = session.query(JoinORM).filter_by(audit_status='completed').all()

        if not joins or len(joins) < 2:
            return PerformanceMetricsSchema(
                total_bets=len(joins) if joins else 0, win_rate=0, roi_percent=0, net_profit=0,
                confidence_interval=[0, 0], p_value=1.0, sample_size=len(joins) if joins else 0
            )

        pnl_data = [j.pnl_native for j in joins]
        roi_data = [j.roi for j in joins]

        total_bets = len(joins)
        total_wins = sum(1 for pnl in pnl_data if pnl > 0)
        win_rate = (total_wins / total_bets) * 100
        net_profit = sum(pnl_data)
        total_staked = sum([j.stake_used for j in joins])
        roi_percent = (net_profit / total_staked) * 100 if total_staked > 0 else 0

        ci = percentile_bootstrap_ci(roi_data)
        p_val = wilcoxon_p_value(pnl_data)

        return PerformanceMetricsSchema(
            total_bets=total_bets,
            win_rate=win_rate,
            roi_percent=roi_percent,
            net_profit=net_profit,
            confidence_interval=[ci[0], ci[1]],
            p_value=p_val if not np.isnan(p_val) else None,
            sample_size=total_bets
        )
    except SQLAlchemyError as e:
        logging.error("Database error while fetching performance metrics", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logging.error("An unexpected error occurred while fetching performance metrics", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if session:
            session.close()

from .models import HealthCheckResponse
import redis

from . import config

@app.get("/health", response_model=HealthCheckResponse)
def get_health():
    """Returns the health status of the application's critical services."""

    # Check database health
    db_status = "ok"
    try:
        session = get_db_session()
        session.execute(text("SELECT 1"))
        session.close()
    except Exception as e:
        db_status = f"error: {e}"

    # Check Celery (Redis) health
    celery_status = "ok"
    try:
        r = redis.Redis.from_url(config.REDIS_URL, socket_connect_timeout=1)
        r.ping()
    except Exception as e:
        celery_status = f"error: {e}"

    return HealthCheckResponse(
        status="ok" if db_status == "ok" and celery_status == "ok" else "error",
        database=db_status,
        celery=celery_status
    )
