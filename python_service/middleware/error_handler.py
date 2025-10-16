# python_service/middleware/error_handler.py
import structlog
import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from pydantic import ValidationError
import json

from ..core.errors import ErrorCategory

logger = structlog.get_logger(__name__)

def _get_error_category(exc: Exception) -> ErrorCategory:
    """Maps an exception type to a defined ErrorCategory."""
    if isinstance(exc, httpx.RequestError):
        return ErrorCategory.NETWORK_ERROR
    if isinstance(exc, (ValidationError, json.JSONDecodeError)):
        return ErrorCategory.PARSING_ERROR
    # In a more complex system, we could check for specific config errors
    # if isinstance(exc, ConfigNotFoundError): return ErrorCategory.CONFIGURATION_ERROR
    return ErrorCategory.UNEXPECTED_ERROR

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            category = _get_error_category(exc)

            logger.error(
                "unhandled_exception_caught",
                error_category=category.name,
                error_message=str(exc),
                path=request.url.path,
                method=request.method,
                exc_info=True,
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "category": category.name,
                        "message": category.value,
                        "detail": str(exc),
                    }
                },
            )