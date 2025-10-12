# python_service/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import structlog
from datetime import datetime, timedelta

log = structlog.get_logger(__name__)

class ErrorRecoveryMiddleware:
    def __init__(self, app):
        self.app = app
        self.error_counts = {}
        self.circuit_breaker_open = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check circuit breaker before proceeding
        request = Request(scope, receive)
        adapter_name = self._extract_adapter_from_request(request)
        if adapter_name and self._is_circuit_open(adapter_name):
            log.warning("Circuit breaker is open for adapter", adapter=adapter_name)
            response = JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"error": f"Service temporarily unavailable for adapter '{adapter_name}' due to repeated failures."}
            )
            await response(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            # Re-create the request object here to handle the error context
            request_on_error = Request(scope, receive)
            await self._handle_error(request_on_error, exc, send)

    async def _handle_error(self, request: Request, exc: Exception, send):
        error_id = f"{type(exc).__name__}_{datetime.now().timestamp()}"
        log.error("Unhandled error", error_id=error_id, path=request.url.path, error_type=type(exc).__name__, exc_info=True)

        adapter_name = self._extract_adapter_from_request(request)
        if adapter_name:
            self._increment_error_count(adapter_name)
            if self._should_open_circuit(adapter_name):
                log.warning("Circuit breaker opened for adapter", adapter=adapter_name)
                self.circuit_breaker_open[adapter_name] = datetime.now()

        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error", "error_id": error_id}
        )
        # The response must be awaited with the original scope, receive, and send callables
        await response(request.scope, request.receive, send)

    def _extract_adapter_from_request(self, request: Request) -> str | None:
        """Extracts the adapter name from the 'source' query parameter."""
        return request.query_params.get("source")

    def _increment_error_count(self, adapter_name: str):
        if adapter_name not in self.error_counts:
            self.error_counts[adapter_name] = []
        self.error_counts[adapter_name].append(datetime.now())
        cutoff = datetime.now() - timedelta(minutes=5)
        self.error_counts[adapter_name] = [t for t in self.error_counts[adapter_name] if t > cutoff]

    def _should_open_circuit(self, adapter_name: str) -> bool:
        return len(self.error_counts.get(adapter_name, [])) > 5

    def _is_circuit_open(self, adapter_name: str) -> bool:
        if adapter_name not in self.circuit_breaker_open:
            return False
        opened_at = self.circuit_breaker_open[adapter_name]
        if (datetime.now() - opened_at) > timedelta(minutes=10):
            del self.circuit_breaker_open[adapter_name]
            log.info("Circuit breaker auto-closed for adapter", adapter=adapter_name)
            return False
        return True
