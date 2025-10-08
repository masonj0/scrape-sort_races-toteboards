# python_service/config.py

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    API_KEY: str
    BETFAIR_APP_KEY: str = ""
    BETFAIR_USERNAME: str = ""
    BETFAIR_PASSWORD: str = ""
    TVG_API_KEY: str = ""
    RACING_AND_SPORTS_TOKEN: str = ""
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Configuration for restored adapters ---
    GREYHOUND_API_URL: Optional[str] = None
    AT_THE_RACES_KEY: Optional[str] = None
    SPORTING_LIFE_KEY: Optional[str] = None
    TIMEFORM_KEY: Optional[str] = None

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()