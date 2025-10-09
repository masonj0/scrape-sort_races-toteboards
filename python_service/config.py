#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Centralized Configuration
# =================================á=============================================
# This module, restored by the Great Correction, provides a centralized and
# validated source for all application settings using pydantic-settings.
# ==============================================================================

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional

class Settings(BaseSettings):
    # --- Application Security ---
    API_KEY: str

    # --- Betfair API Credentials ---
    BETFAIR_APP_KEY: str = ""
    BETFAIR_USERNAME: str = ""
    BETFAIR_PASSWORD: str = ""

    # --- Other Adapter Keys ---
    TVG_API_KEY: str = ""
    RACING_AND_SPORTS_TOKEN: str = ""
    POINTSBET_API_KEY: str = ""
    GREYHOUND_API_URL: Optional[str] = None
    THE_RACING_API_KEY: Optional[str] = None

    # --- Placeholder keys for restored scrapers (not currently used but good practice) ---
    AT_THE_RACES_KEY: Optional[str] = None
    SPORTING_LIFE_KEY: Optional[str] = None
    TIMEFORM_KEY: Optional[str] = None

    # --- Caching Configuration ---
    REDIS_URL: str = "redis://localhost"

    # --- CORS Configuration ---
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()