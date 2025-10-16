#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Centralized Configuration
# =================================á=============================================
# This module, restored by the Great Correction, provides a centralized and
# validated source for all application settings using pydantic-settings.
# ==============================================================================

from functools import lru_cache
from typing import List
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Core Settings ---
    API_KEY: str

    # --- Optional Betfair Credentials ---
    BETFAIR_APP_KEY: Optional[str] = None
    BETFAIR_USERNAME: Optional[str] = None
    BETFAIR_PASSWORD: Optional[str] = None

    # --- Caching & Performance ---
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 300
    MAX_CONCURRENT_REQUESTS: int = 10
    HTTP_POOL_CONNECTIONS: int = 100
    HTTP_POOL_MAXSIZE: int = 100
    HTTP_MAX_KEEPALIVE: int = 50
    DEFAULT_TIMEOUT: int = 30
    ADAPTER_TIMEOUT: int = 20

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Optional Adapter Keys ---
    TVG_API_KEY: Optional[str] = None
    RACING_AND_SPORTS_TOKEN: Optional[str] = None
    POINTSBET_API_KEY: Optional[str] = None
    GREYHOUND_API_URL: Optional[str] = None
    THE_RACING_API_KEY: Optional[str] = None

    # --- CORS Configuration ---
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
