# ==============================================================================
# == Base Module for Adapters
# ==============================================================================
# This module provides the foundational, shared components for all adapters,
# including data models, the base class, and the resilient fetcher.
# ==============================================================================

import logging
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict
from datetime import datetime
from pydantic import BaseModel, Field

# --- Finalized Data Models ---

class Runner(BaseModel):
    name: str
    odds: Optional[float] = None

class Race(BaseModel):
    race_id: str
    track_name: str
    race_number: Optional[int] = None
    post_time: Optional[datetime] = None
    runners: List[Runner]
    source: Optional[str] = None
    checkmate_score: Optional[float] = None
    is_qualified: Optional[bool] = None
    trifecta_factors_json: Optional[str] = None
    analysis_details: Optional[str] = None # For advanced analysis

# --- Resilient Fetcher ---
class DefensiveFetcher:
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Union[dict, str, None]:
        """
        Executes a curl command to fetch data from a URL, providing a resilient
        and environment-independent way to make HTTP requests.
        """
        try:
            command = ["curl", "-s", "-L", "--tlsv1.2", "--http1.1"]
            if headers:
                for key, value in headers.items():
                    command.extend(["-H", f"{key}: {value}"])
            command.append(url)

            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=15)
            response_text = result.stdout

            try:
                # Attempt to parse as JSON first
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback to returning raw text if not valid JSON
                logging.warning(f"Failed to decode JSON from {url}, returning raw text.")
                return response_text
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"CRITICAL: curl GET failed for {url}. Details: {e}")
            return None

# --- Abstract Base Adapter ---
class BaseAdapterV7(ABC):
    """
    The abstract base class for all V7+ adapters. It requires a fetcher
    and provides a consistent interface for the orchestrator.
    """
    # The SOURCE_ID should be a unique identifier for each adapter implementation.
    SOURCE_ID: str = "base_adapter"

    def __init__(self, fetcher: DefensiveFetcher):
        self.fetcher = fetcher

    @abstractmethod
    def fetch_races(self) -> List[Race]:
        """
        The core method for an adapter. It should fetch data from its source
        and return a list of standardized Race objects.
        """
        raise NotImplementedError