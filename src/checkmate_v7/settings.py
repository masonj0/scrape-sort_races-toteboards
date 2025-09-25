# src/checkmate_v7/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./checkmate_v7.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    QUALIFICATION_SCORE: float = Field(default=70.0, description="The minimum score for a race to be 'qualified'.")
    MIN_FIELD_SIZE: int = Field(default=8, description="Minimum number of runners for a race.")
    MIN_FAV_ODDS: float = Field(default=1.5, description="Minimum odds for the favorite to be considered competitive.")
    MAX_FAV_ODDS: float = Field(default=3.5, description="Maximum odds for the favorite.")
    MIN_2ND_FAV_ODDS: float = Field(default=3.0, description="Minimum odds for the second favorite.")
    MAX_2ND_FAV_ODDS: float = Field(default=9.0, description="Maximum odds for the second favorite.")

    class Config:
        env_file = ".env"
        case_sensitive = False
settings = Settings()