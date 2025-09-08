import random
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_sync_page_content(
    url: str,
    cache_dir: Optional[str] = None,
    headers: Optional[dict] = None,
    **kwargs,
) -> str:
    """
    Fetches the content of a given URL synchronously.

    Args:
        url: The URL to fetch.
        cache_dir: The directory to cache the response in.
        headers: The headers to use for the request.
        **kwargs: Additional keyword arguments to pass to the requests library.

    Returns:
        The content of the page as a string.
    """
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", random.choice(USER_AGENTS))

    response = requests.get(url, headers=headers, **kwargs)
    response.raise_for_status()
    return response.text
