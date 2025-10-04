# python_service/security.py

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
    Verifies that the provided API key matches the one in our settings.
    The settings are injected as a dependency, making this testable.
    """
    if key == settings.API_KEY:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )