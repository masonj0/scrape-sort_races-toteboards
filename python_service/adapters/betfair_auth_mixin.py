# python_service/adapters/betfair_auth_mixin.py

from datetime import datetime
from datetime import timedelta
from typing import Optional

import httpx
import structlog

log = structlog.get_logger(__name__)


class BetfairAuthMixin:
    """Encapsulates Betfair authentication logic for reuse across adapters."""

    session_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

    async def _authenticate(self, http_client: httpx.AsyncClient):
        if self.session_token and self.token_expiry and self.token_expiry > (datetime.now() + timedelta(minutes=5)):
            return
        if not all([self.app_key, self.config.BETFAIR_USERNAME, self.config.BETFAIR_PASSWORD]):
            raise ValueError("Betfair credentials not fully configured.")

        auth_url = "https://identitysso.betfair.com/api/login"
        headers = {"X-Application": self.app_key, "Content-Type": "application/x-www-form-urlencoded"}
        payload = f"username={self.config.BETFAIR_USERNAME}&password={self.config.BETFAIR_PASSWORD}"

        log.info(f"{self.__class__.__name__}: Authenticating...")
        response = await http_client.post(auth_url, headers=headers, content=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "SUCCESS":
            self.session_token = data.get("token")
            self.token_expiry = datetime.now() + timedelta(hours=3)
        else:
            raise ConnectionError(f"Betfair authentication failed: {data.get('error')}")
