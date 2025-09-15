### **ARCHITECTURAL MANDATE V7.1**
**Project:** Checkmate V3: The Asynchronous Web Application
**Status:** LOCKED & FINAL (Revised)
**Date:** 2025-09-15

## 1.0 Abstract & Guiding Principles

### 1.1 Mission

This document is the **final, locked architectural specification** for the Checkmate V3 project. It is required reading for all AI teammates and serves as the single source of truth for the system's design.

### 1.2 Architectural Verdict

The V7 architecture is validated as cohesive, pragmatic, and production-ready. Its core strengths are **Strong Separation of Concerns**, **Asynchronous Rigor**, **Statistical Honesty**, **Resilient & Ethical Data Acquisition**, and **Controlled Complexity**.

### 1.3 The Five Pillars

The system **MUST** be implemented across five Python files:
*   `models.py` - **THE BLUEPRINT** (Data Structures & Contracts)
*   `logic.py` - **THE BRAIN** (Pure, Stateless Analysis)
*   `services.py` - **THE GATEWAY** (Asynchronous I/O & Background Tasks)
*   `api.py` - **THE CONDUCTOR** (Stateless HTTP Interface)
*   `dashboard.py` - **THE FACE** (Thin-Client User Interface)

### 1.4 Guiding Policies

All implementation work must adhere to policies for **Configuration via Environment**, **Comprehensive Structured Logging**, and **Graceful Error Handling**.

### 1.5 The Modernization Mandate (CRITICAL CLARIFICATION)

This document specifies a **target architecture**, not a ground-up reimplementation. The primary directive for the implementation agent is to **refactor and transplant** existing, proven logic from the project's historical codebase into the new five-file structure.

**This is a modernization project, NOT a "start from scratch" project.**

*   The analytical core of the **`logic.py`** file **MUST** be derived from the battle-tested logic within `golden_script/checkmate_python.py`.
*   The data acquisition patterns for the **`services.py`** file **MUST** be built upon the collective wisdom and specific implementations found in the `src/paddock_parser/adapters/` directory.
*   The goal is to pour the "old wine" of our proven logic into the "new bottles" of this superior, decoupled architecture, hardening and adapting it as we go.

---

## 2.0 The Five-File Implementation Specification

### 2.1 FILE: `models.py` - The Canonical Data Blueprint

**ROLE:** Defines the database schema (ORM) and API data contracts (Schemas).

```python
# --- SQLAlchemy ORM Models (The Database Schema) ---
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class PredictionORM(Base):
    __tablename__ = "predictions"
    prediction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    race_key = Column(String, nullable=False, index=True) # Non-unique to allow multiple predictions for the same race over time
    created_at = Column(DateTime, nullable=False)
    model_version = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    odds_snapshots = Column(JSON)
    score_components = Column(JSON)
    qualitative_analysis = Column(JSON)
    qualified_flag = Column(Boolean, nullable=False)
    stake_used = Column(Float, nullable=False)
    join = relationship("JoinORM", back_populates="prediction", uselist=False)

class ResultORM(Base):
    __tablename__ = "results"
    result_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    race_key = Column(String, nullable=False, index=True)
    exact_time_off = Column(DateTime)
    result_source_adapter = Column(String)
    audit_version = Column(Integer, default=1)
    post_time_favorite_selection_id = Column(String)
    place_paid_flag = Column(Boolean)
    place_payout_native = Column(Float)
    audit_status = Column(String, nullable=False, index=True) # e.g., 'completed', 'conflict'
    join = relationship("JoinORM", back_populates="result", uselist=False)

class JoinORM(Base):
    __tablename__ = "joins"
    join_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String, ForeignKey("predictions.prediction_id"), unique=True)
    result_id = Column(String, ForeignKey("results.result_id"), unique=True)
    pnl_usd = Column(Float)
    roi = Column(Float)
    audit_notes = Column(String)
    prediction = relationship("PredictionORM", back_populates="join")
    result = relationship("ResultORM", back_populates="join")

class SettingsORM(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, default=1)
    llm_analysis_enabled = Column(Boolean, nullable=False, default=False)

class AdapterStatusORM(Base):
    __tablename__ = "adapter_status"
    adapter_id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="OK")
    last_ok_at = Column(DateTime)
    error_count = Column(Integer, default=0)

# --- Pydantic Schemas (The API Data Contracts) ---
from pydantic import BaseModel
from typing import List, Tuple, Optional
import datetime

class PredictionSchema(BaseModel):
    prediction_id: str
    race_key: str
    status: str
    qualified_flag: bool
    stake_used: float

    class Config:
        from_orm = True

class PerformanceMetricsSchema(BaseModel):
    total_bets: int
    win_rate: float
    net_pnl_usd: float
    roi_percentage: float
    sample_size_n: int
    roi_confidence_interval: Optional[Tuple[float, float]]
    p_value: Optional[float]

class ActionStatusSchema(BaseModel):
    status: str
    message: str
    task_id: str

class HealthCheckResponse(BaseModel):
    api_status: str
    database_status: str
    celery_status: str
```

### 2.2 FILE: `logic.py` - The Pure Analytical Core

**ROLE:** Contains the stateless, deterministic "Brain" of the application.

```python
# This file imports from models.py but no other project files.
import json
from pydantic import ValidationError # Example for error handling

class AdvancedPlaceBetAnalyzer:
    """Performs all quantitative analysis on a given race.
    SOURCE MATERIAL: The core analytical functions from golden_script/checkmate_python.py
    """
    def identify_favorite_with_confidence(self, runners: list) -> tuple:
        # Logic to find the favorite and determine confidence from odds gaps.
        pass

    def calculate_sophisticated_place_probability(self, favorite, race) -> float:
        # Complex, stateless math for probability calculation based on odds, field size, etc.
        pass

    def run_full_analysis(self, race) -> dict:
        # Orchestrates the quantitative analysis steps.
        pass

class LLMQualitativeAnalyzer:
    """Augments quantitative scores with LLM-based qualitative analysis."""
    def __init__(self, llm_client):
        """The LLM client is injected to allow for easy mocking and testing."""
        self.llm_client = llm_client

    def analyze_qualitative_factors(self, race, quantitative_analysis: dict) -> dict:
        """Builds a detailed prompt, calls the LLM, and parses the response."""
        prompt = self._build_prompt(race, quantitative_analysis)

        try:
            raw_response = self.llm_client.get_completion(prompt)
            return self._parse_and_constrain(raw_response)
        except (json.JSONDecodeError, ValidationError) as e:
            log_error("LLM response parsing failed.", error=e, raw_response=raw_response)
            return {"multiplier": 1.0, "confidence": 0.0, "insights": [], "risks": ["LLM parsing error"]}

    def _parse_and_constrain(self, response: str) -> dict:
        # ... logic to parse JSON, validate schema, and clamp values to safe ranges ...
        pass
```

### 2.3 FILE: `services.py` - The Asynchronous Background Worker

**ROLE:** Executes all long-running, blocking, and asynchronous tasks.

```python
from celery import Celery
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import RequestException
from .models import SessionLocal, PredictionORM, SettingsORM
from .logic import AdvancedPlaceBetAnalyzer, LLMQualitativeAnalyzer

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

# In production, this should be a shared cache like Redis.
LLM_CACHE = {}

# SOURCE MATERIAL: The DefensiveFetcher and various adapter classes in src/paddock_parser/adapters/
# provide the patterns for the classes below.
class DefensiveFetcher: ...
class DataSourceOrchestrator: ...

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, soft_time_limit=300, time_limit=360)
def run_prediction_cycle_task(self):
    """Fetches upcoming races, analyzes them, and saves predictions."""
    db = None
    try:
        db = SessionLocal()
        # ... orchestrator and analyzer setup ...

        races = orchestrator.fetch_all_races()
        for race in races:
            # Prevent duplicate pending predictions for the same race key.
            existing = db.query(PredictionORM).filter_by(race_key=race.race_key, status='pending').first()
            if existing: continue
            # ... rest of analysis and saving logic ...
        db.commit()
    except (SQLAlchemyError, RequestException) as e:
        log_critical("Task failed, will retry.", task_name=self.name, error=e)
        raise self.retry(exc=e)
    finally:
        if db: db.close()

# ... other tasks like run_audit_cycle_task ...
```

### 2.4 FILE: `api.py` - The Central API Server

**ROLE:** Provides a clean, stateless HTTP interface to the system.

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import numpy as np
from scipy.stats import wilcoxon
from . import models, services

app = FastAPI()

# Dependency for getting a DB session
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_percentile_bootstrap_ci(data: list, n_resamples=10000, ci=0.95) -> Optional[tuple]:
    if len(data) < 30: return None
    data_array = np.array(data)
    bootstrapped_means = [np.mean(np.random.choice(data_array, size=len(data_array), replace=True)) for _ in range(n_resamples)]
    alpha = (1 - ci) / 2
    return (np.percentile(bootstrapped_means, alpha * 100), np.percentile(bootstrapped_means, (1 - alpha) * 100))

def calculate_wilcoxon_p_value(data: list) -> Optional[float]:
    if len(data) < 10: return None
    stat, p_value = wilcoxon(data, alternative='greater')
    return p_value

@app.get("/api/v1/performance", response_model=models.PerformanceMetricsSchema)
def get_performance_metrics(db: Session = Depends(get_db)):
    # ... logic to query joins, calculate stats, CI, and p-value ...
    pass

@app.post("/api/v1/actions/start_monitoring", response_model=models.ActionStatusSchema)
def start_monitoring():
    task = services.run_prediction_cycle_task.delay()
    return {"status": "dispatched", "message": "Prediction cycle started.", "task_id": task.id}

@app.get("/api/v1/health", response_model=models.HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    # ... logic to check DB and Celery health ...
    pass
```

### 2.5 FILE: `dashboard.py` - The Interactive User Interface

**ROLE:** Provides a pure, stateless web client for the operator.

```python
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(layout="wide")
st.title("Checkmate V3: Closed-Loop ROI System")

# --- Sidebar ---
with st.sidebar:
    st.header("Control Panel")
    if st.button("Run Prediction Cycle"):
        # ... POST request to start monitoring ...
    st.header("Performance Metrics")
    perf_container = st.container()
    st.header("System Health")
    health_container = st.container()

# --- Main Dashboard ---
st.header("Active Predictions")
predictions_placeholder = st.empty()

def update_dashboard():
    # Update Performance Metrics from the API
    perf_response = requests.get(f"{API_URL}/performance")
    if perf_response.ok:
        metrics = perf_response.json()
        ci = metrics.get('roi_confidence_interval')
        if ci and ci[0] is not None:
             display_string = f"ROI: {metrics['roi_percentage']:.2f}% (95% CI: [{ci[0]:.2f}%, {ci[1]:.2f}%], n={metrics['sample_size_n']}, p={metrics['p_value']:.3f})"
        else:
            display_string = f"ROI: {metrics['roi_percentage']:.2f}% (n={metrics['sample_size_n']}, insufficient data for CI)"
        perf_container.text(display_string)

    # Update System Health from the API
    health_response = requests.get(f"{API_URL}/health")
    if health_response.ok:
        # ... display health metrics ...
        pass

# Initial page load
update_dashboard()
```

---

## 3.0 Operational & Deployment Considerations

*   **1. Celery Task Management:** All tasks will have timeouts and retry policies. A dead letter queue will be configured for tasks that fail repeatedly.
*   **2. LLM Cost Control & Caching:** A shared Redis cache will be used to prevent redundant API calls across multiple workers.
*   **3. Health Checks & Observability:** The `/health` endpoint provides a readiness check. Structured JSON logs will be used for integration with a log aggregation service.
