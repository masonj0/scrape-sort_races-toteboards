import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./checkmate_v7.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
