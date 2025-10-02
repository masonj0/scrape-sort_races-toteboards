# python_service/adapters/betfair_adapter.py

import os
import requests
import logging
from datetime import datetime, timedelta

class BetfairAdapter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = "https://api.betfair.com/exchange/betting/rest/v1.0/"
        self.auth_url = "https://identitysso.betfair.com/api/login"
        self.app_key = os.getenv('BETFAIR_APP_KEY')
        self.username = os.getenv('BETFAIR_USERNAME')
        self.password = os.getenv('BETFAIR_PASSWORD')
        self.session_token = None
        self.token_expires_at = None

    def _authenticate(self):
        """Authenticate with Betfair API and get a session token."""
        if not all([self.app_key, self.username, self.password]):
            self.logger.warning("Betfair credentials not fully configured. Skipping auth.")
            return False

        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        payload = f'username={self.username}&password={self.password}'

        try:
            response = requests.post(self.auth_url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'SUCCESS':
                self.session_token = data.get('token')
                self.token_expires_at = datetime.now() + timedelta(hours=4)
                self.logger.info("Successfully authenticated with Betfair.")
                return True
            else:
                self.logger.error(f"Betfair authentication failed: {data.get('error')}")
                return False
        except requests.RequestException as e:
            self.logger.error(f"Error during Betfair authentication: {e}")
            return False

    def _ensure_authenticated(self):
        """Check token validity and refresh if needed."""
        if not self.session_token or datetime.now() >= self.token_expires_at:
            self.logger.info("Betfair session token expired or missing. Re-authenticating...")
            return self._authenticate()
        return True

    def fetch_races(self):
        """Fetch races from Betfair."""
        if not self._ensure_authenticated():
            return [] # Cannot proceed without authentication

        # Placeholder for actual race fetching logic
        # This part would use the session_token to make authenticated calls
        self.logger.info("Betfair adapter is authenticated and would fetch races here.")
        return [] # Returning empty list until race fetch logic is implemented