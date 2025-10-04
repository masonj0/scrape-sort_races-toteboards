# python_service/config.py

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Defines all required environment variables. Fails on startup if any are missing."""
    # API Keys - Add all required keys here
    BETFAIR_APP_KEY: str
    BETFAIR_USERNAME: str
    BETFAIR_PASSWORD: str

    # Optional keys with default values
    TVG_API_KEY: Optional[str] = None
    RACING_AND_SPORTS_TOKEN: Optional[str] = None
    POINTSBET_API_KEY: Optional[str] = None

    # Security Settings
    API_KEY: str

    class Config:
        env_file = ".env"

# Use a cached function to create a single settings instance
@lru_cache()
def get_settings():
    return Settings()