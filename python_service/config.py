# python_service/config.py
import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache
import structlog

# --- Encryption Setup ---
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_ENABLED = True
except ImportError:
    ENCRYPTION_ENABLED = False

KEY_FILE = Path('.key')
CIPHER = None
if ENCRYPTION_ENABLED and KEY_FILE.exists():
    with open(KEY_FILE, 'rb') as f:
        key = f.read()
    CIPHER = Fernet(key)

def decrypt_value(value: Optional[str]) -> Optional[str]:
    """If a value is encrypted, decrypts it. Otherwise, returns it as is."""
    if value and value.startswith('encrypted:') and CIPHER:
        try:
            return CIPHER.decrypt(value[10:].encode()).decode()
        except Exception:
            # Return the corrupted value for debugging, but it will likely fail later
            return value
    return value

from .credentials_manager import SecureCredentialsManager

class Settings(BaseSettings):
    API_KEY: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        # If .env doesn't have API_KEY, try to load from credential manager
        if not self.API_KEY:
            self.API_KEY = SecureCredentialsManager.get_api_key() or "MISSING"

    # --- Optional Betfair Credentials ---
    BETFAIR_APP_KEY: Optional[str] = None
    BETFAIR_USERNAME: Optional[str] = None
    BETFAIR_PASSWORD: Optional[str] = None

    # --- Caching & Performance ---
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 1800  # 30 minutes
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

    def __init__(self, **values):
        super().__init__(**values)
        # Decrypt sensitive fields after initial loading
        self.BETFAIR_APP_KEY = decrypt_value(self.BETFAIR_APP_KEY)
        self.BETFAIR_USERNAME = decrypt_value(self.BETFAIR_USERNAME)
        self.BETFAIR_PASSWORD = decrypt_value(self.BETFAIR_PASSWORD)


@lru_cache()
def get_settings() -> Settings:
    """Loads settings and performs a proactive check for legacy paths."""
    log = structlog.get_logger(__name__)
    if ENCRYPTION_ENABLED and not KEY_FILE.exists():
        log.warning("encryption_key_not_found", file=str(KEY_FILE), recommendation="Run 'python manage_secrets.py' to generate a key.")

    settings = Settings()

    # --- Legacy Path Detection ---
    legacy_paths = ["attic/", "checkmate_web/", "vba_source/"]
    for path in legacy_paths:
        if os.path.exists(path):
            log.warning(
                "legacy_path_detected",
                path=path,
                recommendation="This directory is obsolete and should be removed for optimal performance and security."
            )

    return settings