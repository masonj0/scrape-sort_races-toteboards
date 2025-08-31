import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from paddock_parser.http_client import ForagerClient

@pytest.mark.anyio
@patch("random.choice")
@patch("httpx.AsyncClient")
async def test_forager_client_uses_random_user_agent(mock_async_client, mock_random_choice):
    """
    Tests that the ForagerClient's fetch method uses a randomly selected User-Agent.
    """
    # --- Setup ---
    # 1. Mock the response object that client.get() will return
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock() # This is a regular method, not awaited
    mock_response.text = "<html></html>"

    # 2. Mock the client instance that the 'async with' will yield
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = mock_response # .get() returns our response mock

    # 3. Set up the async context manager
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # 4. Mock random.choice
    test_user_agent = "Test-User-Agent-123"
    mock_random_choice.return_value = test_user_agent

    forager = ForagerClient()
    test_url = "http://example.com"

    # --- Run ---
    await forager.fetch(test_url)

    # --- Assertions ---
    mock_random_choice.assert_called_once_with(ForagerClient.USER_AGENTS)
    expected_headers = {"User-Agent": test_user_agent}
    mock_client_instance.get.assert_called_once_with(test_url, headers=expected_headers, follow_redirects=True)

@pytest.mark.anyio
@patch("paddock_parser.http_client.asyncio.sleep", return_value=None)
@patch("httpx.AsyncClient")
async def test_forager_client_retries_on_failure(mock_async_client, mock_sleep):
    """
    Tests that the ForagerClient's fetch method retries on transient errors.
    """
    # --- Setup ---
    # 1. Mock the client to fail twice, then succeed
    mock_client_instance = AsyncMock()

    # Create a mock for the successful response
    mock_success_response = MagicMock()
    mock_success_response.raise_for_status = MagicMock()
    mock_success_response.text = "Success"

    mock_client_instance.get.side_effect = [
        httpx.RequestError("Connection failed"),
        httpx.HTTPStatusError("Server error", request=MagicMock(), response=MagicMock(status_code=503)),
        mock_success_response
    ]
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Use a client with known retry settings for the test
    forager = ForagerClient(max_retries=3, backoff_factor=0.1)
    test_url = "http://example.com"

    # --- Run ---
    result = await forager.fetch(test_url)

    # --- Assertions ---
    assert result == "Success"

    # Check that fetch was attempted 3 times (1 initial + 2 retries)
    assert mock_client_instance.get.call_count == 3

    # Check that asyncio.sleep was called with the correct backoff times
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(0.1 * (2 ** 0))
    mock_sleep.assert_any_call(0.1 * (2 ** 1))
