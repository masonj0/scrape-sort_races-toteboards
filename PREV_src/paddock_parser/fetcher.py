import anyio
import random
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
]

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True,
    sleep=anyio.sleep,
)
async def get_page_content(url: str, post_data: dict = None) -> str:
    """
    Asynchronously fetches the content of a web page with retries and realistic headers.
    Can perform either a GET or a POST request.
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    async with httpx.AsyncClient() as client:
        if post_data:
            response = await client.post(url, headers=headers, json=post_data, timeout=30.0)
        else:
            response = await client.get(url, headers=headers, timeout=30.0)

        response.raise_for_status()
        return response.text