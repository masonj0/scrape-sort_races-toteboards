# python_service/security.py

import secrets
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader

from .config import Settings, get_settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(
    key: str = Security(api_key_header),
    settings: Settings = Depends(get_settings)
):
    """
    Verifies the provided API key against the one in settings using a
    timing-attack resistant comparison.
    """
    if secrets.compare_digest(key, settings.API_KEY):
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )