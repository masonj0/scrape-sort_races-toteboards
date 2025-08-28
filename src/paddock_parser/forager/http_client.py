import httpx

class HTTPClient:
    """
    A simple HTTP client to fetch data from web sources.
    This is a placeholder for the high-performance Go/Rust forager.
    """

    def __init__(self):
        self.client = httpx.Client()

    def fetch(self, url: str) -> str:
        """
        Fetches the content of a URL.
        """
        try:
            response = self.client.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            return ""
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            return ""
