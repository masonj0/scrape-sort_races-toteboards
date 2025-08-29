import httpx

async def fetch_html_content(url: str) -> str:
    """
    Fetches HTML content from a URL using an async HTTP client.
    """
    try:
        async with httpx.AsyncClient() as client:
            # SkySports may block default user agents, so let's use a common one.
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.text
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}: {e}")
        return ""
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
        return ""
