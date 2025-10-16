# python_service/adapters/base.py
import httpx
import structlog
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

class BaseAdapter:
    """The base class for all data adapters, now with enhanced error handling."""

    def __init__(self, source_name: str, base_url: str = "", config: dict = None):
        self.source_name = source_name
        self.base_url = base_url
        self.config = config or {}
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.retryer = AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        # Circuit Breaker State
        self.circuit_breaker_tripped = False
        self.circuit_breaker_failure_count = 0
        self.circuit_breaker_last_failure = 0
        self.FAILURE_THRESHOLD = 3
        self.COOLDOWN_PERIOD_SECONDS = 300  # 5 minutes

    async def make_request(self, http_client: httpx.AsyncClient, method: str, url: str, **kwargs):
        full_url = url if url.startswith('http') else f"{self.base_url}{url}"

        async def _make_request():
            response = await http_client.request(method, full_url, **kwargs)
            response.raise_for_status()
            # Note: Previously, this returned response.json(), but that prevents
            # the Timeform adapter from reading .text for HTML parsing.
            # Returning the full response object is more flexible.
            return response

        try:
            async for attempt in self.retryer:
                with attempt:
                    return await _make_request()
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "http_error",
                adapter=self.source_name,
                status_code=e.response.status_code,
                url=full_url,
            )
            self._show_windows_toast(
                "Adapter HTTP Error", f"{self.source_name}: Received status {e.response.status_code} from {full_url}"
            )
            return None
        except httpx.RequestError as e:
            self.logger.error("request_error", adapter=self.source_name, error=str(e), url=full_url)
            self._show_windows_toast("Adapter Network Error", f"{self.source_name}: Could not connect to {full_url}")
            return None
        except Exception as e:
            self.logger.error("unexpected_adapter_error", adapter=self.source_name, error=str(e), exc_info=True)
            self._show_windows_toast("Adapter Unexpected Error", f"{self.source_name}: An unknown error occurred.")
            return None

    def _show_windows_toast(self, title: str, message: str):
        try:
            from windows_toasts import Toast, WindowsToaster
            toaster = WindowsToaster(title)
            new_toast = Toast()
            new_toast.text_fields = [message]
            toaster.show_toast(new_toast)
        except (ImportError, RuntimeError):
            # Fail silently if not on Windows or if notifier fails
            pass