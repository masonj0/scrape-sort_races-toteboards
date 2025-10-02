import pytest
import requests
import os

# Set the host for the tests
API_HOST = os.getenv("API_HOST", "http://localhost:5000")

def test_api_funnel_endpoint_returns_success_and_valid_structure():
    """
    SPEC: The /api/funnel endpoint should return a successful response
    with a valid JSON structure containing funnel statistics.

    This is a live integration test that verifies the new Funnel Vision
    endpoint is functioning correctly.
    """
    # 1. ARRANGE
    # The API is assumed to be running. We construct the request URL.
    url = f"{API_HOST}/api/funnel"

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

    # Assert that the response contains the expected keys.
    # The initial response might be "stale" if the main /api/races endpoint hasn't been hit yet.
    if response_json.get("status") == "stale":
        assert "message" in response_json, "Stale response should have a 'message' key."
    else:
        expected_keys = [
            "races_fetched_by_source",
            "total_races_fetched",
            "races_after_deduplication",
            "races_after_scoring",
            "qualified_races",
        ]
        for key in expected_keys:
            assert key in response_json, f"Response JSON is missing expected key: '{key}'"

        assert isinstance(response_json["races_fetched_by_source"], dict), "'races_fetched_by_source' should be a dictionary."