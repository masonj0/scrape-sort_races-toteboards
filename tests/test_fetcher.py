import asyncio
from unittest.mock import patch, MagicMock

import pytest
import httpx
import requests

from paddock_parser.fetcher import get_page_content
from paddock_parser.sync_fetcher import get_sync_page_content

@pytest.mark.anyio
async def test_get_page_content_success():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Hello</h1></body></html>"
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        content = await get_page_content("http://example.com")
        assert content == "<html><body><h1>Hello</h1></body></html>"

@pytest.mark.anyio
async def test_get_page_content_retry_on_failure():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = [
            httpx.RequestError("network error"),
            httpx.RequestError("network error"),
            MagicMock(text="success", raise_for_status=MagicMock()),
        ]
        content = await get_page_content("http://example.com")
        assert content == "success"
        assert mock_client.return_value.__aenter__.return_value.get.call_count == 3


def test_get_sync_page_content_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Hello</h1></body></html>"
        mock_response.raise_for_status = MagicMock()

        mock_get.return_value = mock_response

        content = get_sync_page_content("http://example.com")
        assert content == "<html><body><h1>Hello</h1></body></html>"

def test_get_sync_page_content_retry_on_failure():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            requests.exceptions.RequestException("network error"),
            requests.exceptions.RequestException("network error"),
            MagicMock(text="success", raise_for_status=MagicMock()),
        ]

        content = get_sync_page_content("http://example.com")
        assert content == "success"
        assert mock_get.call_count == 3
