import random
import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .fetcher import USER_AGENTS

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError))
)
def post_json_content(url: str, json_payload: dict) -> requests.Response:
    """
    Posts a JSON payload to a URL with a rotating user agent, realistic headers,
    randomized rate limiting, and a retry mechanism.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "content-type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    # Randomized rate limiting ("jitter")
    time.sleep(random.uniform(0.5, 1.5))

    response = requests.post(url, json=json_payload, headers=headers, timeout=15.0)
    response.raise_for_status()
    return response
