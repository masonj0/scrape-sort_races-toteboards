import pytest
import requests
import os

# Set the host for the tests
API_HOST = os.getenv("API_HOST", "http://localhost:5000")

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