# python_service/api.py

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import EngineManager

app = FastAPI(
    title="Checkmate Ultimate Solo API",
    description="Aggregates horse racing odds from multiple sources.",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)

engine = EngineManager()
background_task = None

@app.on_event("startup")
async def startup_event():
    global background_task
    background_task = asyncio.create_task(engine.run())

@app.on_event("shutdown")
async def shutdown_event():
    global background_task
    if background_task:
        background_task.cancel()
        try: await background_task
        except asyncio.CancelledError: pass
    await engine.close_adapters()

@app.get("/health")
async def health_check(): return {"status": "healthy"}

@app.get("/races")
async def get_races(): return engine.get_last_races()

@app.get("/dashboard")
async def get_dashboard(): return engine.get_dashboard_summary()

@app.get("/funnel")
async def get_funnel(): return engine.get_funnel_statistics()