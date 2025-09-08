import pytest
import httpx
from unittest.mock import AsyncMock, patch

from src.paddock_parser.fetcher import get_page_content

@pytest.mark.anyio
async def test_get_page_content_success():
    """
    SPEC: `get_page_content` should return the text content of a successful response.
    """
    url = "http://test.com"
    request = httpx.Request("GET", url)
    expected_content = "<html>Success</html>"

    # Create a mock response object that includes the request context.
    # This is necessary for the `raise_for_status` method to work correctly.
    mock_response = httpx.Response(200, text=expected_content, request=request)

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock, return_value=mock_response) as mock_get:
        content = await get_page_content(url)
        assert content == expected_content
        mock_get.assert_called_once()

@pytest.mark.anyio
async def test_get_page_content_post_success():
    """
    SPEC: `get_page_content` should handle POST requests correctly.
    """
    url = "http://test.com/post"
    request = httpx.Request("POST", url)
    post_data = {"key": "value"}
    expected_content = "Post Success"

    mock_response = httpx.Response(200, text=expected_content, request=request)

    with patch('httpx.AsyncClient.post', new_callable=AsyncMock, return_value=mock_response) as mock_post:
        content = await get_page_content(url, post_data=post_data)
        assert content == expected_content
        mock_post.assert_called_once_with(url, headers=mock_post.call_args[1]['headers'], json=post_data, timeout=30.0)

@pytest.mark.anyio
async def test_get_page_content_retry_on_http_error():
    """
    SPEC: `get_page_content` should retry on HTTP status errors (e.g., 503).
    """
    url = "http://test.com/retry"
    request = httpx.Request("GET", url)

    # Configure the mock's side_effect to simulate a failure followed by a success.
    mock_responses = [
        httpx.Response(503, request=request),
        httpx.Response(200, text="Success after retry", request=request)
    ]

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock, side_effect=mock_responses) as mock_get:
        content = await get_page_content(url)
        assert content == "Success after retry"
        assert mock_get.call_count == 2

@pytest.mark.anyio
async def test_get_page_content_retry_on_request_error():
    """
    SPEC: `get_page_content` should retry on network-related request errors.
    """
    url = "http://test.com/network-error"
    request = httpx.Request("GET", url)

    # Configure the side_effect to simulate a network error, then a successful response.
    side_effects = [
        httpx.RequestError("Network Error", request=request),
        httpx.Response(200, text="Success after network error", request=request)
    ]

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock, side_effect=side_effects) as mock_get:
        content = await get_page_content(url)
        assert content == "Success after network error"
        assert mock_get.call_count == 2

@pytest.mark.anyio
async def test_get_page_content_fails_after_max_retries():
    """
    SPEC: `get_page_content` should raise the exception after the final retry attempt fails.
    """
    url = "http://test.com/persistent-failure"
    request = httpx.Request("GET", url)

    # Configure the side_effect to consistently raise an HTTPStatusError.
    # This simulates a persistent server-side failure.
    side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=request,
        response=httpx.Response(500, request=request)
    )

    with patch('httpx.AsyncClient.get', new_callable=AsyncMock, side_effect=side_effect) as mock_get:
        with pytest.raises(httpx.HTTPStatusError):
            await get_page_content(url)

        # The tenacity decorator is configured to try 5 times in total.
        assert mock_get.call_count == 5
