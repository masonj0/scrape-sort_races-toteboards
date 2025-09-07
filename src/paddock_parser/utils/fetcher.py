import asyncio
import random
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_page_content(
    url: str,
    cache_dir: Optional[str] = None,
    headers: Optional[dict] = None,
    **kwargs,
) -> str:
    """
    Fetches the content of a given URL.

    Args:
        url: The URL to fetch.
        cache_dir: The directory to cache the response in.
        headers: The headers to use for the request.
        **kwargs: Additional keyword arguments to pass to the HTTPX client.

    Returns:
        The content of the page as a string.
    """
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", random.choice(USER_AGENTS))

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, **kwargs)
        response.raise_for_status()
        await asyncio.sleep(random.uniform(1, 3))
        return response.text
