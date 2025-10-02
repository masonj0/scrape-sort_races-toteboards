import pytest
import requests
import os

# Set the host for the tests
API_HOST = os.getenv("API_HOST", "http://localhost:5001")

def test_api_races_endpoint_returns_success():
    """
    SPEC: The /api/races endpoint should return a successful response.

    This is a live integration test that verifies the entire backend stack
    is functioning correctly, from the API endpoint to the engine and adapters.
    """
    # 1. ARRANGE
    # The API is assumed to be running. We construct the request URL.
    url = f"{API_HOST}/api/races"

    # 2. ACT
    # We make a GET request to the endpoint.
    response = requests.get(url)

    # 3. ASSERT
    # Assert that the request was successful.
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Assert that the response is valid JSON.
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("Response is not valid JSON.")

    # Assert that the response is a list (the new format).
    assert isinstance(response_json, list), f"Expected response to be a list, but got {type(response_json)}"


def test_api_dashboard_endpoint_returns_success():
    """
    SPEC: The /api/dashboard endpoint should return a successful summary.

    This test first warms the cache by calling /api/races, then verifies
    the structure and content of the dashboard summary.
    """
    # 1. ARRANGE
    # Warm the cache by calling the races endpoint first.
    races_url = f"{API_HOST}/api/races"
    requests.get(races_url) # We don't need to assert this, the other test covers it.

    # Now construct the request URL for the dashboard.
    dashboard_url = f"{API_HOST}/api/dashboard"

    # 2. ACT
    # We make a GET request to the endpoint.
    response = requests.get(dashboard_url)

    # 3. ASSERT
    # Assert that the request was successful.
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Assert that the response is valid JSON.
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("Response is not valid JSON.")

    # Assert that the response has the correct 'ok' status and structure.
    assert response_json.get('status') == 'ok', "Dashboard status was not 'ok'."
    assert "last_updated" in response_json
    assert "cache_expires_in_seconds" in response_json
    assert "total_races" in response_json
    assert "total_runners" in response_json
    assert "active_sources" in response_json