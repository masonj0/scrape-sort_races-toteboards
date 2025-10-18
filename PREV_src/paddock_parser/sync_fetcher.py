import random
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
]

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)
def post_page_content(url: str, post_data: dict) -> dict:
    """
    Synchronously sends a POST request with retries and realistic headers.
    Returns the JSON response as a dictionary.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, json=post_data, timeout=30.0)
    response.raise_for_status()
    return response.json()
