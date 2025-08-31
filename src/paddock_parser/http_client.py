import httpx
import random
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ForagerClient:
    """
    A robust data fetching client with User-Agent rotation and retry mechanism.
    """
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    ]

    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def fetch(self, url: str) -> str:
        """
        Fetches HTML content from a URL using an async HTTP client, with a
        randomly selected User-Agent and exponential backoff for retries.
        """
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "User-Agent": random.choice(self.USER_AGENTS)
                    }
                    response = await client.get(url, headers=headers, follow_redirects=True)
                    response.raise_for_status()
                    return response.text
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exception = e
                if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                    logging.warning(f"Client error {e.response.status_code} for {url}. Not retrying.")
                    break

                logging.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}. Retrying...")
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    await asyncio.sleep(wait_time)

        logging.error(f"All {self.max_retries} attempts failed for {url}. Last error: {last_exception}")
        return ""
