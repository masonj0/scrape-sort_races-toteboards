# src/checkmate_v7/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///./checkmate_v7.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    LOG_LEVEL: str = Field(default="INFO")

    # Set a more realistic qualification score
    QUALIFICATION_SCORE: float = Field(default=75.0, description="Minimum score to qualify.")

    # Granular Field Size Scoring
    FIELD_SIZE_OPTIMAL_MIN: int = Field(default=4)
    FIELD_SIZE_OPTIMAL_MAX: int = Field(default=6)
    FIELD_SIZE_ACCEPTABLE_MIN: int = Field(default=7)
    FIELD_SIZE_ACCEPTABLE_MAX: int = Field(default=8)

    FIELD_SIZE_OPTIMAL_POINTS: int = Field(default=30)
    FIELD_SIZE_ACCEPTABLE_POINTS: int = Field(default=10)
    FIELD_SIZE_PENALTY_POINTS: int = Field(default=-20)

    # Favorite & Contention Scoring
    FAV_ODDS_POINTS: int = Field(default=30)
    MAX_FAV_ODDS: float = Field(default=3.5)

    SECOND_FAV_ODDS_POINTS: int = Field(default=40)
    MIN_2ND_FAV_ODDS: float = Field(default=4.0)

    class Config:
        env_file = ".env"
        case_sensitive = False
settings = Settings()